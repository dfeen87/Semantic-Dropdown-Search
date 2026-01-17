"""
Text indexing for Semantic Dropdown Search.

This module pairs text content with semantic descriptors and manages
an in-memory indexed content collection.

Indexing logic is intentionally simple and deterministic.
No ranking, scoring, or inference is performed here.
"""

from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import uuid

from ..core.descriptor import SemanticDescriptor
from ..core.errors import IndexingError


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
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    content_hash: str = field(default="")
    
    def __post_init__(self):
        """Generate content hash if not provided."""
        if not self.content_hash:
            self.content_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Compute SHA-256 hash of text content."""
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()
    
    def update_text(self, new_text: str):
        """Update text content and refresh hash and timestamp."""
        self.text = new_text
        self.content_hash = self._compute_hash()
        self.updated_at = datetime.utcnow()
    
    def update_descriptor(self, new_descriptor: SemanticDescriptor):
        """Update semantic descriptor and refresh timestamp."""
        self.descriptor = new_descriptor
        self.updated_at = datetime.utcnow()
    
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
        id: Optional[str] = None,
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
        
        if id is None:
            id = str(uuid.uuid4())
        
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        
        if not allow_duplicates and content_hash in self._hash_to_id:
            existing_id = self._hash_to_id[content_hash]
            raise IndexingError(
                f"Duplicate content detected (existing id: {existing_id})"
            )
        
        item = IndexedText(
            id=id,
            text=text,
            descriptor=descriptor,
            metadata=metadata or {},
            content_hash=content_hash,
        )
        
        self._items[id] = item
        self._hash_to_id[content_hash] = id
        
        return item
    
    def get(self, id: str) -> Optional[IndexedText]:
        """Retrieve indexed text by ID."""
        return self._items.get(id)
    
    def remove(self, id: str) -> bool:
        """Remove indexed text by ID."""
        item = self._items.pop(id, None)
        if item:
            self._hash_to_id.pop(item.content_hash, None)
            return True
        return False
    
    def update(
        self,
        id: str,
        text: Optional[str] = None,
        descriptor: Optional[SemanticDescriptor] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[IndexedText]:
        """Update an indexed text item."""
        item = self._items.get(id)
        if not item:
            return None
        
        if text is not None:
            self._hash_to_id.pop(item.content_hash, None)
            item.update_text(text)
            self._hash_to_id[item.content_hash] = id
        
        if descriptor is not None:
            if self.validate_on_add:
                result = descriptor.validate(schema_version=self.schema_version)
                if not result:
                    raise IndexingError(
                        "Descriptor validation failed: "
                        + "; ".join(result.errors)
                    )
            item.update_descriptor(descriptor)
        
        if metadata is not None:
            item.metadata.update(metadata)
            item.updated_at = datetime.utcnow()
        
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
        return [
            item
            for item in self._items.values()
            if (value := item.descriptor.get_field(field_name))
            and value.startswith(prefix)
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
        
        for item_data in data:
            item = IndexedText.from_dict(item_data)
            index._items[item.id] = item
            index._hash_to_id[item.content_hash] = item.id
        
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
