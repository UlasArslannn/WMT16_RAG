"""
COMET evaluation for machine translation.

COMET (Crosslingual Optimized Metric for Evaluation of Translation) is a
neural metric that takes source, hypothesis, and reference as input.

Model used: Unbabel/wmt22-comet-da (reference-based, DA = Direct Assessment)

Usage:
    from modules.evaluation import load_comet_model, compute_comet, evaluate_all

    comet_model = load_comet_model()
    result = compute_comet(sources, hypotheses, references, comet_model)
    print(result["system_score"])
"""

import json
import os

COMET_MODEL_NAME = "Unbabel/wmt22-comet-da"


def load_comet_model(model_name: str = COMET_MODEL_NAME):
    """
    Download and load the COMET evaluation model.

    wmt22-comet-da is the standard reference-based COMET model for WMT evaluations.
    It requires source sentences, MT hypotheses, and reference translations.

    Returns:
        COMET model object
    """
    from comet import download_model, load_from_checkpoint

    print(f"Loading COMET model: {model_name}")
    model_path = download_model(model_name)
    model = load_from_checkpoint(model_path)
    print("COMET model ready.")
    return model


def compute_comet(
    sources: list[str],
    hypotheses: list[str],
    references: list[str],
    comet_model,
    batch_size: int = 8,
    gpus: int = 1,
) -> dict:
    """
    Compute COMET scores for a set of translations.

    Args:
        sources: English source sentences
        hypotheses: model-generated Turkish translations
        references: reference Turkish translations
        comet_model: loaded COMET model
        batch_size: scoring batch size
        gpus: number of GPUs (0 for CPU)

    Returns:
        dict with:
            "scores": list of per-sentence float scores
            "system_score": float — corpus-level average
    """
    data = [
        {"src": src, "mt": hyp, "ref": ref}
        for src, hyp, ref in zip(sources, hypotheses, references)
    ]

    results = comet_model.predict(data, batch_size=batch_size, gpus=gpus)

    return {
        "scores": results.scores,
        "system_score": results.system_score,
    }


def evaluate_all(
    approaches: dict[str, list[str]],
    sources: list[str],
    references: list[str],
    comet_model,
    save_path: str = None,
) -> dict[str, float]:
    """
    Evaluate multiple translation approaches with COMET.

    Args:
        approaches: {"approach_name": [translations_list]}
        sources: source sentences
        references: reference translations
        comet_model: loaded COMET model
        save_path: optional JSON path to save results

    Returns:
        dict of {approach_name: system_score}
    """
    results = {}
    for name, hypotheses in approaches.items():
        print(f"\nEvaluating: {name}")
        scores = compute_comet(sources, hypotheses, references, comet_model)
        results[name] = scores["system_score"]
        print(f"  COMET system score: {scores['system_score']:.4f}")

    if save_path:
        os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
        with open(save_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved → {save_path}")

    return results


def print_results_table(results: dict[str, float]) -> None:
    """Pretty-print a comparison table of COMET scores."""
    print("\n" + "=" * 45)
    print(f"{'Approach':<30} {'COMET':>10}")
    print("=" * 45)
    for name, score in sorted(results.items(), key=lambda x: x[1], reverse=True):
        print(f"{name:<30} {score:>10.4f}")
    print("=" * 45)
