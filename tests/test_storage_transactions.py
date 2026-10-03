"""Regression tests for serializable, final-state storage transactions."""

import copy
from threading import Event, Lock, Thread

import numpy as np
import pytest

from api.storage import InMemoryBackend
from core import SemanticDescriptor
from core.errors import IndexingError
from indexer import create_indexed_text


def _item(item_id: str, text: str):
    item = create_indexed_text(
        text,
        SemanticDescriptor(domain="Science", intent="Research"),
        metadata={"source": item_id},
    )
    item.id = item_id
    return item


def _state(backend):
    index, embeddings = backend.get_state_snapshot()
    records = {item.id: item.to_dict() for item in index.get_all()}
    vectors = {item_id: vector.tolist() for item_id, vector in embeddings.items()}
    return records, vectors, dict(index._hash_to_id)


@pytest.mark.parametrize("reverse", [False, True])
def test_existing_ids_can_atomically_swap_hashes_and_embeddings(reverse):
    backend = InMemoryBackend()
    backend.store_items(
        [_item("a", "alpha"), _item("b", "beta"), _item("keep", "unrelated")],
        [np.array([1.0, 0.0]), np.array([0.0, 1.0]), np.array([0.5, 0.5])],
    )
    replacements = [_item("a", "beta"), _item("b", "alpha")]
    vectors = [np.array([2.0, 0.0]), np.array([0.0, 2.0])]
    pairs = list(zip(replacements, vectors))
    if reverse:
        pairs.reverse()

    backend.store_items([pair[0] for pair in pairs], [pair[1] for pair in pairs])

    records, embeddings, hashes = _state(backend)
    assert {item_id: record["text"] for item_id, record in records.items()} == {
        "a": "beta",
        "b": "alpha",
        "keep": "unrelated",
    }
    assert embeddings == {
        "a": [2.0, 0.0],
        "b": [0.0, 2.0],
        "keep": [0.5, 0.5],
    }
    assert hashes == {
        record["content_hash"]: item_id for item_id, record in records.items()
    }


def test_released_hash_can_be_reused_in_same_batch_in_any_order():
    replacements = [_item("a", "new content"), _item("c", "released content")]
    initial = [_item("a", "released content"), _item("keep", "unrelated")]
    expected = None

    for incoming in (replacements, list(reversed(replacements))):
        backend = InMemoryBackend()
        backend.store_items(
            copy.deepcopy(initial),
            [np.array([1.0]), np.array([9.0])],
        )
        vectors_by_id = {"a": np.array([2.0]), "c": np.array([3.0])}
        backend.store_items(incoming, [vectors_by_id[item.id] for item in incoming])
        state = _state(backend)
        if expected is None:
            expected = state
        else:
            assert state == expected

    assert expected[1] == {"a": [2.0], "keep": [9.0], "c": [3.0]}


def test_duplicate_content_final_state_rolls_back_index_and_embeddings():
    backend = InMemoryBackend()
    backend.store_items(
        [_item("a", "alpha"), _item("keep", "unrelated")],
        [np.array([1.0, 0.0]), np.array([0.5, 0.5])],
    )
    before = _state(backend)

    with pytest.raises(IndexingError, match="Duplicate content"):
        backend.store_items(
            [_item("a", "duplicate"), _item("b", "duplicate")],
            [np.array([2.0, 0.0]), np.array([0.0, 2.0])],
        )

    assert _state(backend) == before


def test_backend_detaches_records_embeddings_and_read_snapshots():
    backend = InMemoryBackend()
    item = _item("a", "alpha")
    vector = np.array([1.0, 2.0])
    backend.store_item(item, vector)

    item.text = "caller mutation"
    item.metadata["source"] = "caller mutation"
    vector[:] = 99
    returned_item = backend.get_all_items()[0]
    returned_item.text = "read mutation"
    returned_vector = backend.get_embeddings(["a"])["a"]
    returned_vector[:] = 88

    records, embeddings, _ = _state(backend)
    assert records["a"]["text"] == "alpha"
    assert records["a"]["metadata"] == {"source": "a"}
    assert embeddings["a"] == [1.0, 2.0]


class _ControlledBackend(InMemoryBackend):
    """Expose events only in this test subclass; production locking stays private."""

    def __init__(self):
        super().__init__()
        self.first_inside = Event()
        self.release_first = Event()
        self._calls_lock = Lock()
        self._calls = 0

    def _owned_item(self, item):
        with self._calls_lock:
            self._calls += 1
            call = self._calls
        if call == 1:
            self.first_inside.set()
            assert self.release_first.wait(timeout=5)
        return super()._owned_item(item)


def test_concurrent_batches_serialize_without_lost_updates():
    backend = _ControlledBackend()
    # Seed directly through the base implementation before enabling the hook.
    backend._calls = -1
    backend.store_item(_item("keep", "unrelated"), np.array([9.0, 9.0]))
    backend._calls = 0
    second_started = Event()
    errors = []

    def commit(item_id, text, vector, started=None):
        if started:
            started.set()
        try:
            backend.store_item(_item(item_id, text), np.array(vector))
        except Exception as exc:  # pragma: no cover - asserted below
            errors.append(exc)

    first = Thread(target=commit, args=("a", "alpha", [1.0, 0.0]))
    second = Thread(
        target=commit,
        args=("b", "beta", [0.0, 1.0], second_started),
    )
    first.start()
    assert backend.first_inside.wait(timeout=5)
    second.start()
    assert second_started.wait(timeout=5)
    backend.release_first.set()
    first.join(timeout=5)
    second.join(timeout=5)

    assert not first.is_alive() and not second.is_alive()
    assert errors == []
    records, embeddings, hashes = _state(backend)
    assert set(records) == {"keep", "a", "b"}
    assert embeddings == {
        "keep": [9.0, 9.0],
        "a": [1.0, 0.0],
        "b": [0.0, 1.0],
    }
    assert hashes == {
        record["content_hash"]: item_id for item_id, record in records.items()
    }


def test_concurrent_same_id_uses_transaction_lock_order_last_commit_wins():
    backend = _ControlledBackend()
    second_started = Event()

    first = Thread(
        target=lambda: backend.store_item(_item("shared", "first"), np.array([1.0]))
    )

    def second_commit():
        second_started.set()
        backend.store_item(_item("shared", "second"), np.array([2.0]))

    second = Thread(target=second_commit)
    first.start()
    assert backend.first_inside.wait(timeout=5)
    second.start()
    assert second_started.wait(timeout=5)
    backend.release_first.set()
    first.join(timeout=5)
    second.join(timeout=5)

    records, embeddings, _ = _state(backend)
    assert records["shared"]["text"] == "second"
    assert embeddings["shared"] == [2.0]
