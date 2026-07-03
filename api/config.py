from typing import Literal
from pydantic import BaseModel, Field

class APIConfig(BaseModel):
    engine_mode: Literal["deterministic", "embedding", "hybrid"] = Field(
        default="deterministic",
        description="Mode of the search engine: deterministic, embedding, or hybrid."
    )
    embedding_enabled: bool = Field(
        default=False,
        description="Whether to use the embedding model."
    )
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Name or path of the embedding model to use."
    )
    max_results: int = Field(
        default=10,
        description="Maximum number of results to return per query."
    )
    fallback_keyword_search: bool = Field(
        default=True,
        description="Whether to fallback to keyword search if other methods fail or have low scores."
    )
    storage_backend: Literal["memory", "sqlite"] = Field(
        default="memory",
        description="Which storage backend to use for indexing and retrieval."
    )

config = APIConfig()
