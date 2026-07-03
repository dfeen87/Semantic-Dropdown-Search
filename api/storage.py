from typing import Protocol, List, Optional, Dict, Any
import numpy as np

from indexer.index_text import IndexedText, TextIndex

class StorageBackend(Protocol):
    def store_item(self, item: IndexedText, embedding: Optional[np.ndarray] = None) -> None:
        """Stores a single item and its optional embedding."""
        ...

    def get_all_items(self) -> List[IndexedText]:
        """Returns all stored items."""
        ...

    def get_embeddings(self, item_ids: List[str]) -> Dict[str, np.ndarray]:
        """Returns embeddings for given item IDs. Only returns IDs that have embeddings."""
        ...

    def clear(self) -> None:
        """Clears all stored items."""
        ...

class InMemoryBackend:
    def __init__(self):
        self._index = TextIndex()
        self._embeddings: Dict[str, np.ndarray] = {}

    def store_item(self, item: IndexedText, embedding: Optional[np.ndarray] = None) -> None:
        # Avoid duplicate validation by checking if it already exists, or just catch it
        if self._index.get(item.id):
            self._index.update(
                item_id=item.id,
                text=item.text,
                descriptor=item.descriptor,
                metadata=item.metadata
            )
        else:
            self._index.bulk_load([item]) # Bypasses dedup for simplicity in API ingestion

        if embedding is not None:
            self._embeddings[item.id] = embedding

    def get_all_items(self) -> List[IndexedText]:
        return self._index.get_all()

    def get_embeddings(self, item_ids: List[str]) -> Dict[str, np.ndarray]:
        return {item_id: self._embeddings[item_id] for item_id in item_ids if item_id in self._embeddings}

    def clear(self) -> None:
        self._index.clear()
        self._embeddings.clear()

    def get_text_index(self) -> TextIndex:
        return self._index
