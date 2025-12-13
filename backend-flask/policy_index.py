import json
import os
from functools import lru_cache
from typing import List, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from flask import current_app


def _load_model(model_name: str):
    return SentenceTransformer(model_name)


@lru_cache(maxsize=1)
def _get_model():
    model_name = current_app.config['POLICY_EMBED_MODEL']
    return _load_model(model_name)


def _ensure_paths():
    index_path = current_app.config['POLICY_INDEX_PATH']
    meta_path = current_app.config['POLICY_META_PATH']
    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        raise FileNotFoundError("Policy index or metadata not found. Run ingest_policies.py first.")
    return index_path, meta_path


@lru_cache(maxsize=1)
def _load_index():
    index_path, meta_path = _ensure_paths()
    index = faiss.read_index(index_path)
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    return index, meta


def embed_texts(texts: List[str]) -> np.ndarray:
    model = _get_model()
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return embeddings.astype('float32')


def search(query: str, top_k: int = 5) -> List[dict]:
    index, meta = _load_index()
    query_vec = embed_texts([query])
    scores, idxs = index.search(query_vec, top_k)
    results: List[dict] = []
    for score, idx in zip(scores[0], idxs[0]):
        if idx < 0 or idx >= len(meta):
            continue
        item = meta[idx]
        results.append({
            "text": item.get("text", ""),
            "source": item.get("source", ""),
            "ref": item.get("ref", ""),
            "score": float(score)
        })
    return results

