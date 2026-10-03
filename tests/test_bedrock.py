"""Regression proofs for the v3 BEDROCK state and trust boundaries."""

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from api.config import config
from api.embeddings import compute_similarity
from api.main import app, storage
from core import SemanticDescriptor
from core.errors import IndexingError
from indexer import IndexedText, TextIndex


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_api_state():
    storage.clear()
    defaults = {
        "engine_mode": "deterministic",
        "embedding_enabled": False,
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "max_results": 10,
        "fallback_keyword_search": True,
    }
    for name, value in defaults.items():
        setattr(config, name, value)
    yield


def _item(item_id: str, text: str, descriptor=None) -> IndexedText:
    now = datetime.now(timezone.utc)
    return IndexedText(
        id=item_id,
        text=text,
        descriptor=descriptor or SemanticDescriptor(domain="Science", intent="Research"),
        created_at=now,
        updated_at=now,
    )


def test_failed_multi_field_update_is_atomic():
    index = TextIndex()
    original = index.add(
        "original", SemanticDescriptor(domain="Science", intent="Research")
    )
    original_timestamp = original.updated_at

    with pytest.raises(IndexingError):
        index.update(
            original.id,
            text="mutated",
            descriptor=SemanticDescriptor(domain="not in schema", intent="Research"),
        )

    assert original.text == "original"
    assert original.content_hash == hashlib.sha256(b"original").hexdigest()
    assert original.updated_at == original_timestamp


def test_malformed_metadata_cannot_partially_update_text():
    index = TextIndex()
    original = index.add(
        "original", SemanticDescriptor(domain="Science", intent="Research")
    )

    with pytest.raises(IndexingError, match="metadata"):
        index.update(original.id, text="mutated", metadata=["not", "a", "mapping"])

    assert original.text == "original"


def test_bulk_load_failure_does_not_partially_commit():
    index = TextIndex()
    index.add("existing", SemanticDescriptor(domain="Science", intent="Research"))

    with pytest.raises(IndexingError):
        index.bulk_load([
            _item("valid", "valid"),
            _item(
                "invalid",
                "invalid",
                SemanticDescriptor(domain="unknown", intent="Research"),
            ),
        ])

    assert index.count() == 1
    assert index.get("valid") is None


def test_deserialization_rejects_tampered_content_hash():
    now = datetime.now(timezone.utc).isoformat()
    with pytest.raises(IndexingError, match="content_hash"):
        IndexedText.from_dict({
            "id": "tampered",
            "text": "actual text",
            "descriptor": {"domain": "Science", "intent": "Research"},
            "metadata": {},
            "created_at": now,
            "updated_at": now,
            "content_hash": hashlib.sha256(b"different text").hexdigest(),
        })


def test_deserialization_rejects_naive_timestamps():
    with pytest.raises(IndexingError, match="timezone"):
        IndexedText.from_dict({
            "id": "naive",
            "text": "text",
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-01T00:00:00",
        })


def test_api_rejects_invalid_descriptor_without_storing_any_batch_item():
    response = client.post("/semantic-index", json={"items": [
        {
            "id": "valid",
            "text": "valid",
            "descriptor": {"domain": "Science", "intent": "Research"},
        },
        {
            "id": "invalid",
            "text": "invalid",
            "descriptor": {"domain": "invented", "intent": "Research"},
        },
    ]})

    assert response.status_code == 400
    assert storage.get_all_items() == []


def test_api_rejects_missing_required_descriptor_fields():
    response = client.post("/semantic-index", json={"items": [
        {"id": "missing", "text": "text", "descriptor": {"domain": "Science"}}
    ]})

    assert response.status_code == 400
    assert storage.get_all_items() == []


def test_config_dependency_failure_rolls_back_all_fields(monkeypatch):
    monkeypatch.setattr("api.main.load_embedding_model", lambda _name: False)

    response = client.patch("/semantic-config", json={
        "engine_mode": "hybrid",
        "embedding_enabled": True,
        "embedding_model": "unavailable/model",
        "max_results": 2,
    })

    assert response.status_code == 503
    assert config.engine_mode == "deterministic"
    assert config.embedding_enabled is False
    assert config.embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
    assert config.max_results == 10


def test_api_rejects_duplicate_ids_atomically():
    response = client.post("/semantic-index", json={"items": [
        {
            "id": "same",
            "text": "first",
            "descriptor": {"domain": "Science", "intent": "Research"},
        },
        {
            "id": "same",
            "text": "second",
            "descriptor": {"domain": "Science", "intent": "Research"},
        },
    ]})

    assert response.status_code == 400
    assert storage.get_all_items() == []


@pytest.mark.parametrize(
    "query, documents",
    [
        ([float("nan"), 0.0], [[1.0, 0.0]]),
        ([float("inf"), 0.0], [[1.0, 0.0]]),
        ([1.0, 0.0], [[1.0, float("-inf")]]),
    ],
)
def test_similarity_rejects_non_finite_evidence(query, documents):
    with pytest.raises(ValueError, match="finite"):
        compute_similarity(query, documents)


def test_similarity_rejects_incompatible_dimensions():
    with pytest.raises(ValueError, match="dimensions"):
        compute_similarity([1.0, 0.0], [[1.0, 0.0, 0.0]])


def test_checked_in_openapi_matches_runtime_contract():
    specification = yaml.safe_load(
        (Path(__file__).parents[1] / "api" / "openapi.yaml").read_text(
            encoding="utf-8"
        )
    )

    assert specification == app.openapi()
