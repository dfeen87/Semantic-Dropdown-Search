import logging
from typing import List, Optional
import numpy as np

logger = logging.getLogger(__name__)

_model = None

def load_embedding_model(model_name: str) -> bool:
    """
    Attempts to load the sentence-transformers embedding model.
    Returns True if successful, False otherwise.
    """
    global _model
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(model_name)
        logger.info(f"Successfully loaded embedding model: {model_name}")
        return True
    except ImportError:
        logger.warning("sentence-transformers not installed. Embeddings disabled.")
        return False
    except Exception as e:
        logger.error(f"Failed to load embedding model {model_name}: {e}")
        return False

def compute_embeddings(texts: List[str]) -> Optional[np.ndarray]:
    """
    Computes embeddings for a list of texts using the loaded model.
    Returns a numpy array of embeddings, or None if the model is not loaded.
    """
    global _model
    if _model is None:
        return None
    try:
        embeddings = _model.encode(texts, convert_to_numpy=True)
        return embeddings
    except Exception as e:
        logger.error(f"Failed to compute embeddings: {e}")
        return None

def compute_similarity(query_emb: np.ndarray, doc_embs: np.ndarray) -> np.ndarray:
    """
    Computes cosine similarity between a query embedding and a list of document embeddings.
    """
    # Normalize vectors
    q_norm = np.linalg.norm(query_emb)
    if q_norm == 0:
        return np.zeros(doc_embs.shape[0])

    d_norms = np.linalg.norm(doc_embs, axis=1)

    # Avoid division by zero
    valid_mask = d_norms != 0
    scores = np.zeros(doc_embs.shape[0])

    if np.any(valid_mask):
        scores[valid_mask] = np.dot(doc_embs[valid_mask], query_emb) / (d_norms[valid_mask] * q_norm)

    return scores
