# Copyright (c) Don Michael Feeney Jr.
# Licensed under the MIT License.
import copy
from threading import RLock
from typing import Dict, List, Optional, Protocol, Tuple

import numpy as np

from indexer.index_text import IndexedText, TextIndex


class StorageBackend(Protocol):
    def store_item(self, item: IndexedText, embedding: Optional[np.ndarray] = None) -> None:
        """Stores a single item and its optional embedding."""
        ...

    def get_all_items(self) -> List[IndexedText]:
        """Returns all stored items."""
        ...

    def store_items(
        self,
        items: List[IndexedText],
        embeddings: Optional[List[Optional[np.ndarray]]] = None,
    ) -> None:
        """Atomically stores a batch and its aligned optional embeddings."""
        ...

    def get_embeddings(self, item_ids: List[str]) -> Dict[str, np.ndarray]:
        """Returns embeddings for given item IDs. Only returns IDs that have embeddings."""
        ...

    def get_state_snapshot(self) -> Tuple[TextIndex, Dict[str, np.ndarray]]:
        """Returns a consistent detached index-and-embedding snapshot."""
        ...

    def clear(self) -> None:
        """Clears all stored items."""
        ...


class InMemoryBackend:
    """Thread-safe in-memory storage with serializable batch transactions."""

    def __init__(self):
        self._index = TextIndex()
        self._embeddings: Dict[str, np.ndarray] = {}
        # RLock keeps the synchronization primitive private and makes future
        # locked helpers safe to compose without introducing self-deadlocks.
        self._transaction_lock = RLock()

    @staticmethod
    def _owned_item(item: IndexedText) -> IndexedText:
        """Validate and detach a caller-owned record before storing it."""
        if not isinstance(item, IndexedText):
            raise ValueError("store_items accepts only IndexedText records")
        owned = copy.deepcopy(item)
        # IndexedText is mutable, so callers can invalidate an instance after
        # construction. Re-run all structural/hash/timestamp checks at ingress.
        owned.__post_init__()
        return owned

    @staticmethod
    def _owned_embedding(embedding: np.ndarray) -> np.ndarray:
        """Validate and detach caller-owned embedding evidence."""
        vector = np.array(embedding, copy=True)
        if vector.ndim != 1 or vector.size == 0:
            raise ValueError("each embedding must be a non-empty one-dimensional vector")
        if not np.issubdtype(vector.dtype, np.number):
            raise ValueError("embeddings must contain numeric values")
        if not np.all(np.isfinite(vector)):
            raise ValueError("embeddings must contain only finite values")
        return vector

    def store_item(self, item: IndexedText, embedding: Optional[np.ndarray] = None) -> None:
        self.store_items([item], [embedding])

    def store_items(
        self,
        items: List[IndexedText],
        embeddings: Optional[List[Optional[np.ndarray]]] = None,
    ) -> None:
        """Validate and commit a complete final state as one transaction.

        Transactions are serialized from authoritative-state snapshot through
        commit. Replacements are bulk-loaded together so uniqueness is judged
        against the final collection rather than order-dependent intermediate
        states.
        """
        if embeddings is None:
            embeddings = [None] * len(items)
        if len(embeddings) != len(items):
            raise ValueError("embeddings must align one-to-one with items")

        ids = [item.id for item in items if isinstance(item, IndexedText)]
        if len(ids) != len(items):
            raise ValueError("store_items accepts only IndexedText records")
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate item IDs in one batch are not allowed")

        # The complete snapshot/build/validate/commit boundary is locked. A
        # transaction can therefore never commit a candidate based on stale
        # state after another successful transaction.
        with self._transaction_lock:
            owned_items = [self._owned_item(item) for item in items]
            candidate_index = copy.deepcopy(self._index)
            candidate_index.bulk_load(owned_items)

            candidate_embeddings = {
                item_id: np.array(vector, copy=True)
                for item_id, vector in self._embeddings.items()
            }
            for item, embedding in zip(owned_items, embeddings):
                if embedding is None:
                    # A replacement without new evidence must not retain a
                    # vector representing the prior text.
                    candidate_embeddings.pop(item.id, None)
                else:
                    candidate_embeddings[item.id] = self._owned_embedding(embedding)

            dimensions = {vector.shape[0] for vector in candidate_embeddings.values()}
            if len(dimensions) > 1:
                raise ValueError("stored embedding dimensions must match")

            # Both structures become authoritative while readers are excluded;
            # no reader can observe a cross-transaction mixed state.
            self._index = candidate_index
            self._embeddings = candidate_embeddings

    def get_state_snapshot(self) -> Tuple[TextIndex, Dict[str, np.ndarray]]:
        """Return one detached, transactionally consistent state snapshot."""
        with self._transaction_lock:
            return (
                copy.deepcopy(self._index),
                {
                    item_id: np.array(vector, copy=True)
                    for item_id, vector in self._embeddings.items()
                },
            )

    def get_all_items(self) -> List[IndexedText]:
        index, _ = self.get_state_snapshot()
        return index.get_all()

    def get_embeddings(self, item_ids: List[str]) -> Dict[str, np.ndarray]:
        with self._transaction_lock:
            return {
                item_id: np.array(self._embeddings[item_id], copy=True)
                for item_id in item_ids
                if item_id in self._embeddings
            }

    def clear(self) -> None:
        with self._transaction_lock:
            self._index = TextIndex(
                validate_on_add=self._index.validate_on_add,
                schema_version=self._index.schema_version,
            )
            self._embeddings = {}

    def get_text_index(self) -> TextIndex:
        index, _ = self.get_state_snapshot()
        return index
