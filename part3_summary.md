# Part 3 — Literature Review & Theoretical Background

---

## 3-A. Literature Review: "Exploring Human-Like Translation Strategy with Large Language Models"

### Main Motivation

Professional human translators do not translate word-by-word or sentence-by-sentence in a single pass. They typically follow a multi-stage cognitive process: first analyzing the source text for context and difficulties, producing an initial draft, and then revising that draft for fluency and accuracy. The central hypothesis of the paper is that **LLMs, despite their power, underperform when asked to translate in a single zero-shot pass** because this forces all cognitive steps (understanding, drafting, refining) into one forward pass.

The paper investigates whether instructing LLMs to explicitly **mimic this human-like multi-stage workflow** can yield measurable improvements in translation quality — particularly for complex or low-resource language pairs.

### Proposed Prompting Strategy (MAPS — Multi-Aspect Prompting and Selection)

The paper introduces a pipeline of structured prompting stages:

1. **Pre-translation Analysis**  
   Before translating, the model is asked to identify:
   - Key terminology and domain-specific vocabulary
   - Cultural references that may not have direct equivalents
   - The register and tone of the text (formal, informal, technical)
   - Potential translation pitfalls (idioms, ambiguities)

2. **Draft Translation**  
   Using the analysis as context, the model generates an initial translation. This draft benefits from the explicit planning step.

3. **Refinement / Review (LLM-as-Judge)**  
   The model is then instructed to act as an expert evaluator: it reviews its own draft against criteria of accuracy, fluency, and naturalness, and produces a final refined translation.

4. **Candidate Selection** (in multi-output variants)  
   When multiple candidate translations are generated, a separate LLM call selects the best one by comparing them holistically.

### Key Experimental Findings

- The multi-step MAPS approach **consistently outperforms zero-shot prompting** across multiple language pairs and model families, with gains of 1–3 COMET points on standard WMT benchmarks.
- Improvements are most pronounced for **complex sentences** (longer, with cultural references or ambiguous phrasing) where a single-pass translation is more likely to make systematic errors.
- The strategy is model-agnostic: it improves results even for smaller models (7B–13B) that cannot reliably self-correct under zero-shot prompting.
- The LLM-as-judge step adds the greatest value when the initial draft contains fluency errors, as the critique prompt explicitly surfaces them.

---

## 3-B.1. Prompting Pattern: Break Complex Tasks into Simpler Subtasks

### Definition

"Break Complex Tasks into Simpler Subtasks" is a prompting design pattern where a single complex prompt is replaced by a **chain of simpler, focused prompts**, each responsible for one well-defined sub-task. The output of each step feeds into the next, forming a pipeline.

In the context of machine translation this means splitting the single instruction "translate this sentence" into:
1. Analyze the source text
2. Produce a draft translation
3. Critique and refine the draft

### Why Decomposition Improves Translation Quality

- **Reduced cognitive load per step**: Each prompt focuses the model on one goal, reducing the risk of the model optimizing conflicting objectives simultaneously (e.g., fluency vs. faithfulness vs. cultural adaptation).
- **Explicit intermediate representations**: By externalizing analysis (step 1), the model's "reasoning" about the source text becomes part of the context for drafting — essentially forcing chain-of-thought.
- **Error localization**: Errors introduced in the draft step can be caught and corrected in the refinement step, whereas a single-step error has no recovery mechanism.
- **Better use of model capacity**: For 7B models, handling one well-scoped task at a time is more reliable than handling all tasks in one shot.

### How the Paper Applies This Pattern

The paper structures the translation as three sequential LLM calls (or a single structured prompt with three labeled stages):
- Stage 1 outputs linguistic and cultural notes.
- Stage 2 uses those notes as context to draft the translation.
- Stage 3 reviews the draft against quality criteria and outputs the final version.

This is a direct implementation of the "break complex tasks" pattern applied to the MT pipeline.

---

## 3-B.2. Prompting Pattern: LLM as a Judge

### Definition

"LLM as a Judge" is a prompting pattern where an LLM is used **not to generate the primary output, but to evaluate or select among candidate outputs** produced in a prior step. The LLM acts as a quality assessor, replacing or augmenting traditional automatic metrics.

### How LLMs Evaluate or Refine Candidate Translations

In the MT context:
- **Self-evaluation**: The same LLM that produced the draft is asked to review it against criteria (accuracy, fluency, terminology correctness).
- **Comparative selection**: Multiple candidate translations are presented and the LLM selects the best one with a rationale.
- **Iterative refinement**: The judge's critique is used as a prompt to generate an improved translation.

The judge prompt typically includes explicit evaluation dimensions:
```
Review the following translation for:
(a) Semantic accuracy — does it convey the full meaning?
(b) Fluency — does it read naturally in the target language?
(c) Register — does it match the tone of the source?
Identify any errors and produce an improved version.
```

### Advantages

- **No reference required**: Unlike BLEU or COMET, LLM-as-judge can evaluate quality without human references, enabling use in low-resource scenarios.
- **Holistic evaluation**: Can catch errors that surface-level metrics miss (wrong register, loss of nuance, unnatural phrasing).
- **Actionable feedback**: The critique is itself a prompt for improvement, closing the loop.

### Limitations

- **Positional and verbosity bias**: LLMs tend to favor their own outputs and longer responses.
- **Not calibrated**: Scores are not directly comparable across different models or prompting styles.
- **Computational cost**: Adds an additional inference pass per sentence.
- **Self-referential error propagation**: If the model is systematically wrong about something, its judgment will also be wrong about the same thing.

### Application in the Paper's MT Pipeline

The paper's refinement stage (Step 3) is an instance of LLM-as-judge: the model reviews its own draft, identifies weaknesses along predefined quality axes, and rewrites the translation. In multi-candidate variants, a separate LLM call compares all candidates and selects the best, providing a rationale that explains the selection.

---

## 3-C. Evaluation Metric: COMET vs. BLEU

### COMET — Crosslingual Optimized Metric for Evaluation of Translation

**COMET** is a neural MT evaluation metric trained on human quality judgments (e.g., Direct Assessment scores from WMT campaigns). Unlike lexical metrics, COMET uses a pre-trained multilingual encoder (XLM-R based) to produce semantic representations of the source, hypothesis, and reference, and then predicts a quality score.

#### How COMET Evaluates Translation Quality

The model used in this project is `wmt22-comet-da`, a **reference-based** model:

```
Input:  source sentence (English)
        MT hypothesis (Turkish)
        reference translation (Turkish)

Output: scalar quality score ∈ [0, 1] (higher = better)
```

Internally, the encoder produces contextualized embeddings for all three inputs. A regression head then predicts a quality score calibrated against human DA annotations. The system-level score is the mean over all sentence scores.

Because COMET is trained on human judgments, it captures:
- **Semantic faithfulness** (is the meaning preserved?)
- **Fluency** (does the translation read naturally?)
- **Adequacy** (are all source elements translated?)

#### COMET vs. BLEU

| Aspect | BLEU | COMET |
|---|---|---|
| **Approach** | n-gram overlap (lexical) | Neural regression on human DA scores |
| **Reference needed** | Yes (1+) | Yes (reference-based variant) |
| **Source used** | No | Yes |
| **Semantic understanding** | No | Yes (XLM-R embeddings) |
| **Correlation with humans** | Moderate | High (state-of-the-art) |
| **Interpretability** | High (count-based) | Low (black-box neural) |
| **Score range** | 0–100 (percent) | ~0–1 (calibrated to DA) |
| **Sensitivity to paraphrase** | Low (penalizes valid alternatives) | High (semantically equivalent translations score well) |
| **Low-resource language quality** | Degrades with fewer references | More robust due to multilingual encoder |

**Key takeaway**: BLEU is fast and interpretable but poorly correlated with human judgments on morphologically rich languages like Turkish. COMET is the current standard for WMT evaluation precisely because it handles paraphrase, morphological variation, and cross-lingual semantics that n-gram metrics miss entirely.

---

*This document covers the theoretical background required for Part 3 (A, B.1, B.2, C) of Homework 2.*  
*Experimental results (Part 3-D) are in `notebooks/part3d_prompting.ipynb`.*
