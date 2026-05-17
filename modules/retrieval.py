"""
FAISS-based retrieval for RAG few-shot example selection.

Pipeline:
    1. load_embedding_model()      — load multilingual sentence transformer
    2. build_faiss_index()         — embed corpus + build FAISS index (with caching)
    3. retrieve_examples()         — top-k similar pairs for a query
    4. make_retriever()            — returns a closure for use in translation pipeline

Usage:
    from modules.retrieval import load_embedding_model, build_faiss_index, make_retriever

    emb_model = load_embedding_model()
    index, corpus = build_faiss_index(corpus_pairs, emb_model, index_path="data/faiss_index")
    retriever = make_retriever(index, corpus, emb_model, k=5)

    examples = retriever("The cat sat on the mat.")
"""

import os
import pickle

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def load_embedding_model(model_name: str = DEFAULT_EMBEDDING_MODEL) -> SentenceTransformer:
    """
    Load a multilingual sentence embedding model.

    paraphrase-multilingual-MiniLM-L12-v2 supports 50+ languages including
    both English and Turkish, making it ideal for cross-lingual retrieval.

    Returns:
        SentenceTransformer model
    """
    print(f"Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name)
    print(f"  Embedding dim: {model.get_sentence_embedding_dimension()}")
    return model


def embed_sentences(
    sentences: list[str],
    embedding_model: SentenceTransformer,
    batch_size: int = 64,
    show_progress: bool = True,
) -> np.ndarray:
    """
    Generate L2-normalized embeddings for a list of sentences.

    Args:
        sentences: input sentences
        embedding_model: SentenceTransformer model
        batch_size: encoding batch size
        show_progress: whether to show tqdm bar

    Returns:
        float32 numpy array of shape (N, dim)
    """
    embeddings = embedding_model.encode(
        sentences,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        normalize_embeddings=True,  # L2-normalize → cosine = inner product
    )
    return embeddings.astype(np.float32)


def build_faiss_index(
    corpus_pairs: list[tuple[str, str]],
    embedding_model: SentenceTransformer,
    index_path: str = None,
) -> tuple[faiss.Index, list[tuple[str, str]]]:
    """
    Build a FAISS IndexFlatIP (cosine similarity) from corpus pairs.

    We embed the English (source) side only. At retrieval time, the query
    is also embedded in English, so we find source-similar examples.

    Caching: if index_path is provided and cached files exist, they are loaded
    directly to avoid re-embedding (which can take several minutes on CPU).

    Args:
        corpus_pairs: list of (en, tr) tuples — the full train corpus
        embedding_model: SentenceTransformer model
        index_path: optional base path (without extension) for saving/loading

    Returns:
        (faiss_index, corpus_pairs)
    """
    faiss_file = (index_path + ".faiss") if index_path else None
    pkl_file = (index_path + ".pkl") if index_path else None

    # Try loading from cache
    if faiss_file and os.path.exists(faiss_file) and os.path.exists(pkl_file):
        print(f"Loading cached FAISS index from {index_path}.*")
        index = faiss.read_index(faiss_file)
        with open(pkl_file, "rb") as f:
            corpus_pairs = pickle.load(f)
        print(f"  Index: {index.ntotal} vectors, dim={index.d}")
        return index, corpus_pairs

    print(f"Building FAISS index for {len(corpus_pairs)} pairs...")
    en_sentences = [pair[0] for pair in corpus_pairs]
    embeddings = embed_sentences(en_sentences, embedding_model)

    dim = embeddings.shape[1]
    # IndexFlatIP = exact search with inner product (cosine when vectors are normalized)
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    print(f"  Index built: {index.ntotal} vectors, dim={dim}")

    # Save to disk
    if faiss_file:
        os.makedirs(os.path.dirname(index_path) if os.path.dirname(index_path) else ".", exist_ok=True)
        faiss.write_index(index, faiss_file)
        with open(pkl_file, "wb") as f:
            pickle.dump(corpus_pairs, f)
        print(f"  Index saved to {index_path}.*")

    return index, corpus_pairs


def retrieve_examples(
    query: str,
    index: faiss.Index,
    corpus_pairs: list[tuple[str, str]],
    embedding_model: SentenceTransformer,
    k: int = 5,
) -> list[tuple[str, str]]:
    """
    Retrieve top-k most similar (en, tr) pairs for a query sentence.

    Uses cosine similarity (inner product on L2-normalized vectors).

    Args:
        query: English source sentence
        index: FAISS index
        corpus_pairs: full corpus as (en, tr) list
        embedding_model: SentenceTransformer model
        k: number of examples to retrieve

    Returns:
        list of (en, tr) tuples, most similar first
    """
    query_emb = embed_sentences([query], embedding_model, show_progress=False)
    # Search for k+1 in case the query itself is in the index
    scores, indices = index.search(query_emb, k + 1)

    examples = []
    for idx, score in zip(indices[0], scores[0]):
        if 0 <= idx < len(corpus_pairs):
            examples.append(corpus_pairs[idx])
        if len(examples) == k:
            break

    return examples


def make_retriever(
    index: faiss.Index,
    corpus_pairs: list[tuple[str, str]],
    embedding_model: SentenceTransformer,
    k: int = 5,
):
    """
    Create a retriever callable for use in the translation pipeline.

    Returns:
        retriever(query: str) → list of (en, tr) tuples
    """
    def retriever(query: str) -> list[tuple[str, str]]:
        return retrieve_examples(query, index, corpus_pairs, embedding_model, k=k)

    return retriever
