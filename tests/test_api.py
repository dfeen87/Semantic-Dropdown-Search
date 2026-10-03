# Copyright (c) Don Michael Feeney Jr.
# Licensed under the MIT License.
import numpy as np
import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.config import config
from api.main import storage
from api.storage import InMemoryBackend
from core import SemanticDescriptor
from indexer import create_indexed_text

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_state():
    """Reset storage and config before each test"""
    storage.clear()
    config.engine_mode = "deterministic"
    config.embedding_enabled = False
    config.max_results = 10
    yield

def test_config_endpoints():
    response = client.get("/semantic-config")
    assert response.status_code == 200
    data = response.json()
    assert data["engine_mode"] == "deterministic"

    response = client.patch("/semantic-config", json={"engine_mode": "hybrid"})
    assert response.status_code == 200
    assert response.json()["engine_mode"] == "hybrid"

    response = client.patch("/semantic-config", json={"max_results": -1})
    assert response.status_code == 422
    assert config.max_results == 10


def test_reindex_without_embedding_removes_stale_vector():
    backend = InMemoryBackend()
    item = create_indexed_text(
        "original text",
        SemanticDescriptor(domain="Science", intent="Research"),
    )
    backend.store_item(item, np.array([1.0, 0.0]))

    replacement = create_indexed_text(
        "replacement text",
        SemanticDescriptor(domain="Science", intent="Research"),
    )
    replacement.id = item.id
    backend.store_item(replacement)

    assert backend.get_embeddings([item.id]) == {}


def test_index_and_search_deterministic():
    payload = {
        "items": [
            {
                "id": "doc1",
                "text": "Biology is the study of life",
                "descriptor": {"domain": "Science -> Biology", "intent": "Documentation -> Tutorial"}
            },
            {
                "id": "doc2",
                "text": "Finance deals with money and investments",
                "descriptor": {"domain": "Business", "intent": "Report"}
            }
        ]
    }
    resp = client.post("/semantic-index", json=payload)
    assert resp.status_code == 200
    assert resp.json()["indexed_count"] == 2

    # Search
    resp = client.get("/semantic-search?q=Biology")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == "doc1"
    assert data["results"][0]["score"] == 1.0

def test_index_and_search_hybrid_mocked(monkeypatch):
    monkeypatch.setattr("api.main.load_embedding_model", lambda _name: True)
    monkeypatch.setattr(
        "api.main.compute_embeddings",
        lambda texts: np.array([[1.0, 0.0] for _ in texts]),
    )
    # Force enable embeddings
    client.patch("/semantic-config", json={
        "engine_mode": "hybrid",
        "embedding_enabled": True
    })

    payload = {
        "items": [
            {
                "id": "doc-ai",
                "text": "Artificial intelligence algorithms are complex",
                "descriptor": {"domain": "Science -> Computer Science", "intent": "Research"}
            }
        ]
    }
    resp = client.post("/semantic-index", json=payload)
    assert resp.status_code == 200

    resp = client.get("/semantic-search?q=algorithms")
    assert resp.status_code == 200
    data = resp.json()
    # It should have a score because of the text match fallback, and maybe embedding match
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == "doc-ai"
    assert data["results"][0]["score"] > 0
