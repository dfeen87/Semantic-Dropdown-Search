# Copyright (c) Don Michael Feeney Jr.
# Licensed under the MIT License.
"""
Text indexing for Semantic Dropdown Search.

This module pairs text content with semantic descriptors and manages
an in-memory indexed content collection.

Indexing logic is intentionally simple and deterministic.
No ranking, scoring, or inference is performed here.
"""

from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import uuid

from core.descriptor import SemanticDescriptor
from core.errors import IndexingError


_REQUIRED_SERIALIZATION_KEYS = {"id", "text", "created_at", "updated_at"}


@dataclass
class IndexedText:
    """
    A text object paired with its semantic descriptor.
    
    Attributes:
        id: Unique identifier for this indexed text
        text: The actual text content
        descriptor: Semantic descriptor describing the text
        metadata: Additional metadata (author, title, url, etc.)
        created_at: Timestamp when indexed
        updated_at: Timestamp of last update
        content_hash: SHA-256 hash of text for deduplication
    """
    
    id: str
    text: str
    descriptor: SemanticDescriptor
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    content_hash: str = field(default="")
    
    def __post_init__(self):
        """Validate the record's structural and content-hash invariants."""
        if not isinstance(self.id, str) or not self.id:
            raise IndexingError("Indexed text ID must be a non-empty string")
        if not isinstance(self.text, str):
            raise IndexingError("Indexed text content must be a string")
        if not isinstance(self.descriptor, SemanticDescriptor):
            raise IndexingError("descriptor must be a SemanticDescriptor")
        if not isinstance(self.metadata, dict):
            raise IndexingError("metadata must be a dictionary")
        if not isinstance(self.created_at, datetime) or not isinstance(self.updated_at, datetime):
            raise IndexingError("created_at and updated_at must be datetimes")
        if self.created_at.tzinfo is None or self.updated_at.tzinfo is None:
            raise IndexingError("created_at and updated_at must include a timezone")
        if self.updated_at < self.created_at:
            raise IndexingError("updated_at cannot be earlier than created_at")

        expected_hash = self._compute_hash()
        if self.content_hash and self.content_hash != expected_hash:
            raise IndexingError("content_hash does not match serialized text")
        self.content_hash = expected_hash
    
    def _compute_hash(self) -> str:
        """Compute SHA-256 hash of text content."""
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()
    
    def update_text(self, new_text: str, content_hash: Optional[str] = None):
        """Update text content and refresh hash and timestamp."""
        self.text = new_text
        self.content_hash = content_hash or self._compute_hash()
        self.updated_at = datetime.now(timezone.utc)
    
    def update_descriptor(self, new_descriptor: SemanticDescriptor):
        """Update semantic descriptor and refresh timestamp."""
        self.descriptor = new_descriptor
        self.updated_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "text": self.text,
            "descriptor": self.descriptor.to_dict(),
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "content_hash": self.content_hash,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IndexedText":
        """Create IndexedText from dictionary."""
        missing = _REQUIRED_SERIALIZATION_KEYS - data.keys()
        if missing:
            raise IndexingError(
                f"Missing required keys in serialized data: {missing}"
            )

        descriptor = SemanticDescriptor.from_dict(data.get("descriptor", {}))
        
        return cls(
            id=data["id"],
            text=data["text"],
            descriptor=descriptor,
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            content_hash=data.get("content_hash", ""),
        )


class TextIndex:
    """
    In-memory collection of indexed text objects.
    
    This class deliberately performs no ranking or scoring.
    Persistence is handled externally via adapters.
    """
    
    def __init__(self, validate_on_add: bool = True, schema_version: str = "v1"):
        self.validate_on_add = validate_on_add
        self.schema_version = schema_version
        self._items: Dict[str, IndexedText] = {}
        self._hash_to_id: Dict[str, str] = {}
    
    def add(
        self,
        text: str,
        descriptor: SemanticDescriptor,
        metadata: Optional[Dict[str, Any]] = None,
        item_id: Optional[str] = None,
        allow_duplicates: bool = False,
    ) -> IndexedText:
        """Add text with semantic descriptor to index."""
        
        if self.validate_on_add:
            result = descriptor.validate(schema_version=self.schema_version)
            if not result:
                raise IndexingError(
                    "Descriptor validation failed: "
                    + "; ".join(result.errors)
                )
        
        if item_id is None:
            item_id = str(uuid.uuid4())
        elif item_id in self._items:
            raise IndexingError(
                f"Item with ID '{item_id}' already exists. Use update() instead."
            )
        
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        
        if not allow_duplicates and content_hash in self._hash_to_id:
            existing_id = self._hash_to_id[content_hash]
            raise IndexingError(
                f"Duplicate content detected (existing id: {existing_id})"
            )
        
        item = IndexedText(
            id=item_id,
            text=text,
            descriptor=descriptor,
            metadata=metadata or {},
            content_hash=content_hash,
        )
        
        self._items[item_id] = item
        self._hash_to_id[content_hash] = item_id
        
        return item
    
    def get(self, item_id: str) -> Optional[IndexedText]:
        """Retrieve indexed text by ID."""
        return self._items.get(item_id)
    
    def remove(self, item_id: str) -> bool:
        """Remove indexed text by ID."""
        item = self._items.pop(item_id, None)
        if item:
            self._hash_to_id.pop(item.content_hash, None)
            return True
        return False
    
    def update(
        self,
        item_id: str,
        text: Optional[str] = None,
        descriptor: Optional[SemanticDescriptor] = None,
        metadata: Optional[Dict[str, Any]] = None,
        allow_duplicates: bool = False,
    ) -> Optional[IndexedText]:
        """Update an indexed text item."""
        item = self._items.get(item_id)
        if not item:
            return None

        if descriptor is not None and not isinstance(descriptor, SemanticDescriptor):
            raise IndexingError("descriptor must be a SemanticDescriptor")
        if metadata is not None and not isinstance(metadata, dict):
            raise IndexingError("metadata must be a dictionary")

        # Validate every candidate before mutating the current valid item.  In
        # particular, a bad descriptor must not leave a successful text update
        # behind when both are supplied in one operation.
        if descriptor is not None and self.validate_on_add:
            result = descriptor.validate(schema_version=self.schema_version)
            if not result:
                raise IndexingError(
                    "Descriptor validation failed: " + "; ".join(result.errors)
                )

        new_hash = None
        if text is not None:
            if not isinstance(text, str):
                raise IndexingError("Indexed text content must be a string")
            new_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if not allow_duplicates and new_hash in self._hash_to_id:
                existing_id = self._hash_to_id[new_hash]
                if existing_id != item_id:
                    raise IndexingError(
                        f"Duplicate content detected (existing id: {existing_id})"
                    )
            self._hash_to_id.pop(item.content_hash, None)
            item.update_text(text, content_hash=new_hash)
            self._hash_to_id[new_hash] = item_id
        
        if descriptor is not None:
            item.update_descriptor(descriptor)
        
        if metadata is not None:
            item.metadata.update(metadata)
            item.updated_at = datetime.now(timezone.utc)
        
        return item
    
    def filter_by_field(self, field_name: str, value: str) -> List[IndexedText]:
        """Filter indexed texts by exact field match."""
        return [
            item
            for item in self._items.values()
            if item.descriptor.get_field(field_name) == value
        ]
    
    def filter_by_fields(self, filters: Dict[str, str]) -> List[IndexedText]:
        """Filter indexed texts by multiple fields (AND logic)."""
        results = []
        for item in self._items.values():
            if all(
                item.descriptor.get_field(k) == v
                for k, v in filters.items()
            ):
                results.append(item)
        return results
    
    def filter_by_prefix(self, field_name: str, prefix: str) -> List[IndexedText]:
        """Filter indexed texts by hierarchical prefix."""
        delimiter = f"{prefix} → "
        return [
            item
            for item in self._items.values()
            if (value := item.descriptor.get_field(field_name))
            and (value == prefix or value.startswith(delimiter))
        ]
    
    def get_all(self) -> List[IndexedText]:
        """Return all indexed items."""
        return list(self._items.values())
    
    def get_field_values(self, field_name: str) -> Set[str]:
        """Get all unique values for a given field."""
        return {
            value
            for item in self._items.values()
            if (value := item.descriptor.get_field(field_name)) is not None
        }
    
    def count(self) -> int:
        """Return number of indexed items."""
        return len(self._items)
    
    def bulk_load(self, items: List["IndexedText"]) -> None:
        """Atomically load records after enforcing index invariants.

        Existing IDs may be replaced (the behavior used by storage backends),
        but duplicate IDs or hashes within one incoming batch are rejected.
        Descriptor validation follows ``validate_on_add``.
        """
        candidate_items = dict(self._items)
        incoming_ids = set()
        incoming_hashes = {}

        for item in items:
            if not isinstance(item, IndexedText):
                raise IndexingError("bulk_load accepts only IndexedText records")
            if item.id in incoming_ids:
                raise IndexingError(f"Duplicate item ID in bulk load: '{item.id}'")
            incoming_ids.add(item.id)
            other_id = incoming_hashes.get(item.content_hash)
            if other_id is not None:
                raise IndexingError(
                    f"Duplicate content in bulk load (ids: {other_id}, {item.id})"
                )
            incoming_hashes[item.content_hash] = item.id
            if self.validate_on_add:
                result = item.descriptor.validate(schema_version=self.schema_version)
                if not result:
                    raise IndexingError(
                        "Descriptor validation failed: " + "; ".join(result.errors)
                    )
            candidate_items[item.id] = item

        candidate_hashes = {}
        for item in candidate_items.values():
            existing_id = candidate_hashes.get(item.content_hash)
            if existing_id is not None and existing_id != item.id:
                raise IndexingError(
                    f"Duplicate content detected (ids: {existing_id}, {item.id})"
                )
            candidate_hashes[item.content_hash] = item.id

        self._items = candidate_items
        self._hash_to_id = candidate_hashes
    
    def clear(self):
        """Clear the index."""
        self._items.clear()
        self._hash_to_id.clear()
    
    def to_list(self) -> List[Dict[str, Any]]:
        """Convert index to list of dictionaries."""
        return [item.to_dict() for item in self._items.values()]
    
    @classmethod
    def from_list(
        cls,
        data: List[Dict[str, Any]],
        validate_on_add: bool = True,
        schema_version: str = "v1",
    ) -> "TextIndex":
        """Create TextIndex from serialized list."""
        index = cls(
            validate_on_add=validate_on_add,
            schema_version=schema_version,
        )
        
        items = [IndexedText.from_dict(item_data) for item_data in data]
        index.bulk_load(items)
        
        return index


def create_indexed_text(
    text: str,
    descriptor: SemanticDescriptor,
    metadata: Optional[Dict[str, Any]] = None,
    validate: bool = True,
    schema_version: str = "v1",
) -> IndexedText:
    """Convenience factory for IndexedText."""
    
    if validate:
        result = descriptor.validate(schema_version=schema_version)
        if not result:
            raise IndexingError(
                "Descriptor validation failed: "
                + "; ".join(result.errors)
            )
    
    return IndexedText(
        id=str(uuid.uuid4()),
        text=text,
        descriptor=descriptor,
        metadata=metadata or {},
    )
