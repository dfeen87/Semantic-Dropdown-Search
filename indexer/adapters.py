"""
Storage adapters for Semantic Dropdown Search.

This module provides adapters for persisting indexed texts to various
storage backends (files, directories, memory).

Adapters are intentionally simple and do not implement indexing logic.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
from abc import ABC, abstractmethod

from indexer.index_text import IndexedText, TextIndex
from indexer.serialize import (
    JSONSerializer,
    NDJSONSerializer,
    CSVSerializer,
    save_to_file,
    load_from_file,
)
from core.errors import IndexingError


# -------------------------
# BASE ADAPTER
# -------------------------

class StorageAdapter(ABC):
    """Abstract base class for storage adapters."""

    @abstractmethod
    def save(self, index: TextIndex):
        pass

    @abstractmethod
    def load(self) -> TextIndex:
        pass

    @abstractmethod
    def exists(self) -> bool:
        pass

    @abstractmethod
    def delete(self):
        pass


# -------------------------
# FILE ADAPTER
# -------------------------

class FileAdapter(StorageAdapter):
    """
    File-based storage adapter.

    Supports JSON, NDJSON, and CSV formats.
    """

    def __init__(
        self,
        filepath: Path,
        format: Optional[str] = None,
        validate_on_load: bool = True,
        schema_version: str = "v1",
    ):
        self.filepath = Path(filepath)
        self.format = format or self._detect_format()
        self.validate_on_load = validate_on_load
        self.schema_version = schema_version

    def _detect_format(self) -> str:
        ext = self.filepath.suffix.lstrip(".").lower()
        if ext in {"json"}:
            return "json"
        if ext in {"ndjson", "jsonl"}:
            return "ndjson"
        if ext == "csv":
            return "csv"
        return "json"

    def save(self, index: TextIndex):
        save_to_file(
            index.get_all(),
            self.filepath,
            format=self.format,
        )

    def load(self) -> TextIndex:
        if not self.exists():
            return TextIndex(
                validate_on_add=self.validate_on_load,
                schema_version=self.schema_version,
            )

        items = load_from_file(self.filepath, format=self.format)

        index = TextIndex(
            validate_on_add=False,
            schema_version=self.schema_version,
        )

        for item in items:
            index._items[item.id] = item
            index._hash_to_id[item.content_hash] = item.id

        return index

    def exists(self) -> bool:
        return self.filepath.exists()

    def delete(self):
        if self.exists():
            self.filepath.unlink()

    def append(self, item: IndexedText):
        if self.format != "ndjson":
            raise IndexingError(
                "Append operation only supported for NDJSON format"
            )

        NDJSONSerializer.append_to_file(item, self.filepath)


# -------------------------
# MEMORY ADAPTER
# -------------------------

class MemoryAdapter(StorageAdapter):
    """
    In-memory storage adapter.

    Useful for testing and ephemeral indexes.
    """

    def __init__(
        self,
        validate_on_load: bool = True,
        schema_version: str = "v1",
    ):
        self.validate_on_load = validate_on_load
        self.schema_version = schema_version
        self._storage: Optional[TextIndex] = None

    def save(self, index: TextIndex):
        copy = TextIndex(
            validate_on_add=self.validate_on_load,
            schema_version=self.schema_version,
        )

        for item in index.get_all():
            copy._items[item.id] = item
            copy._hash_to_id[item.content_hash] = item.id

        self._storage = copy

    def load(self) -> TextIndex:
        if self._storage is None:
            return TextIndex(
                validate_on_add=self.validate_on_load,
                schema_version=self.schema_version,
            )
        return self._storage

    def exists(self) -> bool:
        return self._storage is not None

    def delete(self):
        self._storage = None


# -------------------------
# DIRECTORY ADAPTER
# -------------------------

class DirectoryAdapter(StorageAdapter):
    """
    Directory-based storage adapter.

    Stores each indexed text as a separate file.
    """

    def __init__(
        self,
        directory: Path,
        format: str = "json",
        validate_on_load: bool = True,
        schema_version: str = "v1",
    ):
        self.directory = Path(directory)
        self.format = format
        self.validate_on_load = validate_on_load
        self.schema_version = schema_version

    def _item_path(self, item_id: str) -> Path:
        return self.directory / f"{item_id}.{self.format}"

    def save(self, index: TextIndex):
        self.directory.mkdir(parents=True, exist_ok=True)

        for item in index.get_all():
            save_to_file(
                [item],
                self._item_path(item.id),
                format=self.format,
            )

    def load(self) -> TextIndex:
        index = TextIndex(
            validate_on_add=False,
            schema_version=self.schema_version,
        )

        if not self.exists():
            return index

        for path in self.directory.glob(f"*.{self.format}"):
            items = load_from_file(path, format=self.format)
            for item in items:
                index._items[item.id] = item
                index._hash_to_id[item.content_hash] = item.id

        return index

    def exists(self) -> bool:
        return self.directory.exists() and self.directory.is_dir()

    def delete(self):
        if self.exists():
            import shutil
            shutil.rmtree(self.directory)

    def save_item(self, item: IndexedText):
        self.directory.mkdir(parents=True, exist_ok=True)
        save_to_file(
            [item],
            self._item_path(item.id),
            format=self.format,
        )

    def delete_item(self, item_id: str):
        path = self._item_path(item_id)
        if path.exists():
            path.unlink()


# -------------------------
# INDEX MANAGER
# -------------------------

class IndexManager:
    """
    High-level manager for TextIndex with automatic persistence.
    """

    def __init__(self, adapter: StorageAdapter, auto_save: bool = True):
        self.adapter = adapter
        self.auto_save = auto_save
        self._index: Optional[TextIndex] = None

    @property
    def index(self) -> TextIndex:
        if self._index is None:
            self._index = self.adapter.load()
        return self._index

    def add(
        self,
        text: str,
        descriptor,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> IndexedText:
        item = self.index.add(
            text,
            descriptor,
            metadata,
            **kwargs,
        )

        if self.auto_save:
            self.save()

        return item

    def get(self, id: str) -> Optional[IndexedText]:
        return self.index.get(id)

    def remove(self, id: str) -> bool:
        removed = self.index.remove(id)
        if removed and self.auto_save:
            self.save()
        return removed

    def update(self, id: str, **kwargs) -> Optional[IndexedText]:
        item = self.index.update(id, **kwargs)
        if item and self.auto_save:
            self.save()
        return item

    def filter_by_field(self, field_name: str, value: str) -> List[IndexedText]:
        return self.index.filter_by_field(field_name, value)

    def filter_by_fields(self, filters: Dict[str, str]) -> List[IndexedText]:
        return self.index.filter_by_fields(filters)

    def get_all(self) -> List[IndexedText]:
        return self.index.get_all()

    def count(self) -> int:
        return self.index.count()

    def save(self):
        self.adapter.save(self.index)

    def reload(self):
        self._index = self.adapter.load()

    def clear(self):
        self.index.clear()
        if self.auto_save:
            self.save()
