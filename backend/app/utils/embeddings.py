"""
Embedding utility — generates 384-dim vectors using a local sentence-transformer model.
Weights download once on first use (cached under EMBEDDING_CACHE_DIR, default /models).
"""
import logging
import os
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)

_CACHE_DIR = os.environ.get("EMBEDDING_CACHE_DIR", "/models")


@lru_cache(maxsize=1)
def _load_model(model_name: str):
    """Load model once and cache in memory."""
    try:
        os.makedirs(_CACHE_DIR, exist_ok=True)
        from sentence_transformers import SentenceTransformer
        logger.info("Loading embedding model: %s", model_name)
        return SentenceTransformer(model_name, cache_folder=_CACHE_DIR)
    except Exception as exc:
        logger.warning("Could not load embedding model: %s", exc)
        return None


def get_embedding(text: str, model_name: str = "all-MiniLM-L6-v2") -> Optional[list[float]]:
    """
    Return a 384-dim embedding for `text`.
    Returns None if the model failed to load (app still works, just without semantic search).
    """
    model = _load_model(model_name)
    if model is None:
        return None
    try:
        vector = model.encode(text, normalize_embeddings=True)
        return vector.tolist()
    except Exception as exc:
        logger.warning("Embedding generation failed: %s", exc)
        return None
