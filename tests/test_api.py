import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.config import config
from api.main import storage

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_state():
    """Reset storage and config before each test"""
    storage.clear()
    config.engine_mode = "deterministic"
    config.embedding_enabled = False
    yield

def test_config_endpoints():
    response = client.get("/semantic-config")
    assert response.status_code == 200
    data = response.json()
    assert data["engine_mode"] == "deterministic"

    response = client.patch("/semantic-config", json={"engine_mode": "hybrid"})
    assert response.status_code == 200
    assert response.json()["engine_mode"] == "hybrid"

def test_index_and_search_deterministic():
    payload = {
        "items": [
            {
                "id": "doc1",
                "text": "Biology is the study of life",
                "descriptor": {"domain": "Science -> Biology", "intent": "Education"}
            },
            {
                "id": "doc2",
                "text": "Finance deals with money and investments",
                "descriptor": {"domain": "Finance", "intent": "Informational"}
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

def test_index_and_search_hybrid_mocked():
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
                "descriptor": {"domain": "Computer Science", "intent": "Research"}
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
