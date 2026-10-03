# Copyright (c) Don Michael Feeney Jr.
# Licensed under the MIT License.
import numpy as np
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Body, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.descriptor import SemanticDescriptor
from indexer.index_text import create_indexed_text
from query.query_builder import QueryBuilder
from query.predicates import TextContains

from api.config import config, APIConfig
from api.embeddings import load_embedding_model, compute_embeddings, compute_similarity
from api.storage import InMemoryBackend

@asynccontextmanager
async def lifespan(_app):
    """Activate optional dependencies before accepting traffic."""
    if config.embedding_enabled and not load_embedding_model(config.embedding_model):
        raise RuntimeError(f"Embedding model unavailable: {config.embedding_model}")
    yield


app = FastAPI(
    title="Semantic Dropdown Search API",
    description="Deterministic semantic dropdown search, with optional embedding-based enhancement.",
    version="3.0.0",
    lifespan=lifespan,
)

# Enable CORS for browser extensions, search widgets, etc.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize storage
storage = InMemoryBackend()

# --- Models ---

class ItemInput(BaseModel):
    id: Optional[str] = None
    text: str
    tags: Optional[List[str]] = None
    descriptor: Optional[Dict[str, Any]] = None # The semantic descriptor dict

class IndexRequest(BaseModel):
    items: List[ItemInput]

class SearchResult(BaseModel):
    id: str
    text: str
    score: float
    descriptor: Dict[str, Any]

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    mode: str

class SemanticConfigUpdate(BaseModel):
    engine_mode: Optional[str] = None
    embedding_enabled: Optional[bool] = None
    embedding_model: Optional[str] = None
    max_results: Optional[int] = Field(default=None, ge=0)
    fallback_keyword_search: Optional[bool] = None


# --- Endpoints ---

@app.get("/semantic-config", response_model=APIConfig)
def get_config():
    """Returns the current API configuration."""
    return config

@app.patch("/semantic-config", response_model=APIConfig)
def update_config(update: SemanticConfigUpdate):
    """Updates API configuration fields only after dependencies are ready."""
    changes = update.model_dump(exclude_none=True)
    try:
        candidate = config.model_copy(update=changes)
        candidate = APIConfig.model_validate(candidate.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    candidate_model = candidate.embedding_model
    candidate_enabled = candidate.embedding_enabled
    if candidate_enabled and (
        not config.embedding_enabled or candidate_model != config.embedding_model
    ):
        if not load_embedding_model(candidate_model):
            raise HTTPException(
                status_code=503,
                detail=f"Embedding model unavailable: {candidate_model}",
            )

    for field_name, value in candidate.model_dump().items():
        setattr(config, field_name, value)

    return config

@app.post("/semantic-index")
def index_items(request: IndexRequest):
    """
    Indexes a batch of items. Computes embeddings if enabled.
    """
    texts_to_embed = []
    items_to_store = []

    # Process items and build deterministic representations
    for item in request.items:
        desc_dict = item.descriptor or {}

        try:
            descriptor = SemanticDescriptor.from_dict(desc_dict)
            metadata = {}
            if item.tags:
                metadata["tags"] = item.tags
            if item.id:
                metadata["original_id"] = item.id
            indexed_text = create_indexed_text(
                text=item.text,
                descriptor=descriptor,
                metadata=metadata,
                validate=True,
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create indexed text: {str(e)}")

        if item.id:
            indexed_text.id = item.id # override auto-generated uuid

        items_to_store.append(indexed_text)
        texts_to_embed.append(item.text)

    # Compute embeddings if enabled
    embeddings = None
    if config.embedding_enabled and texts_to_embed:
        embeddings = compute_embeddings(texts_to_embed)

    if config.embedding_enabled and texts_to_embed and embeddings is None:
        raise HTTPException(status_code=503, detail="Embedding computation unavailable")
    if embeddings is not None:
        embeddings = np.asarray(embeddings)
        if (
            embeddings.ndim != 2
            or embeddings.shape[0] != len(items_to_store)
            or embeddings.shape[1] == 0
            or not np.all(np.isfinite(embeddings))
        ):
            raise HTTPException(status_code=503, detail="Embedding output is malformed")

    vectors = list(embeddings) if embeddings is not None else None
    try:
        storage.store_items(items_to_store, vectors)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to store batch: {exc}")

    return {"status": "success", "indexed_count": len(items_to_store)}


@app.get("/semantic-search", response_model=SearchResponse)
def search(
    q: str = Query(..., description="The plain-text query to search for"),
    mode: Optional[str] = Query(None, description="Override engine_mode for this request")
):
    """
    Searches indexed content.
    Returns ranked results based on the chosen mode (deterministic, embedding, hybrid).
    """
    effective_mode = mode if mode in ["deterministic", "embedding", "hybrid"] else config.engine_mode

    # One snapshot keeps index records and their embedding evidence aligned
    # even while another request commits a batch concurrently.
    text_index, snapshot_embeddings = storage.get_state_snapshot()
    all_items = text_index.get_all()
    if not all_items:
        return SearchResponse(query=q, results=[], mode=effective_mode)

    results_map = {} # item_id -> SearchResult template (we'll update score)

    # 1. Deterministic Layer (Keyword/Descriptor search fallback if no specific structured query is provided)
    # Since 'q' is plain-text, deterministic search here means a text-contains or keyword match
    # unless we parse 'q' into descriptor filters. For a search bar, text_contains is the baseline.

    deterministic_scores = {}
    if effective_mode in ["deterministic", "hybrid"] or config.fallback_keyword_search:
        qb = QueryBuilder(text_index).where_text_contains(q, case_sensitive=False)
        det_results = qb.execute()

        # Simple scoring: 1.0 for match, 0.0 for no match
        for item in det_results.items:
            deterministic_scores[item.id] = 1.0
            results_map[item.id] = SearchResult(
                id=item.id,
                text=item.text,
                score=1.0,
                descriptor=item.descriptor.to_dict()
            )

    # 2. Embedding Layer
    embedding_scores = {}
    if effective_mode in ["embedding", "hybrid"] and config.embedding_enabled:
        q_emb = compute_embeddings([q])
        if q_emb is not None and len(q_emb) > 0:
            q_vec = q_emb[0]

            # Fetch all items to compute similarity
            item_ids = [item.id for item in all_items]
            embs_dict = {
                item_id: snapshot_embeddings[item_id]
                for item_id in item_ids
                if item_id in snapshot_embeddings
            }

            valid_ids = list(embs_dict.keys())
            if valid_ids:
                doc_embs = np.array([embs_dict[vid] for vid in valid_ids])
                try:
                    sim_scores = compute_similarity(q_vec, doc_embs)
                except ValueError as exc:
                    raise HTTPException(
                        status_code=503,
                        detail=f"Embedding evidence is malformed: {exc}",
                    ) from exc

                for i, vid in enumerate(valid_ids):
                    score = float(sim_scores[i])
                    embedding_scores[vid] = score

                    if vid not in results_map:
                        # Find original item
                        orig_item = next((itm for itm in all_items if itm.id == vid), None)
                        if orig_item:
                            results_map[vid] = SearchResult(
                                id=orig_item.id,
                                text=orig_item.text,
                                score=score,
                                descriptor=orig_item.descriptor.to_dict()
                            )

    # 3. Combine and Rank
    final_results = []

    for vid, res in results_map.items():
        det_score = deterministic_scores.get(vid, 0.0)
        emb_score = embedding_scores.get(vid, 0.0)

        if effective_mode == "deterministic":
            final_score = det_score
        elif effective_mode == "embedding":
            # If embedding search didn't yield a score, fallback to deterministic text match score if enabled
            if emb_score == 0.0 and config.fallback_keyword_search:
                final_score = det_score * 0.1 # Weight it lower to indicate it's a fallback
            else:
                final_score = emb_score
        else: # hybrid
            # Simple weighted blend
            final_score = (det_score * 0.4) + (emb_score * 0.6)

        res.score = final_score

        # Only include if score > 0
        if final_score > 0.0:
            final_results.append(res)

    # Sort by score descending
    final_results.sort(key=lambda x: x.score, reverse=True)

    # Apply limit
    final_results = final_results[:config.max_results]

    return SearchResponse(
        query=q,
        results=final_results,
        mode=effective_mode
    )
