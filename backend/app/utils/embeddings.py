"""
Embedding utility — generates 384-dim vectors using a local sentence-transformer model.
No external API calls; model is downloaded once and cached in /models.
"""
import logging
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _load_model(model_name: str):
    """Load model once and cache in memory."""
    try:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading embedding model: %s", model_name)
        return SentenceTransformer(model_name, cache_folder="/models")
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
