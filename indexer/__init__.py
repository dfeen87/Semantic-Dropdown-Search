"""
Indexer module for Semantic Dropdown Search.

This module provides functionality for indexing text content with
semantic descriptors and persisting to various storage backends.
"""

from .index_text import (
    IndexedText,
    TextIndex,
    create_indexed_text,
)

from .serialize import (
    Serializer,
    JSONSerializer,
    NDJSONSerializer,
    CSVSerializer,
    serialize,
    deserialize,
    save_to_file,
    load_from_file,
)

from .adapters import (
    StorageAdapter,
    FileAdapter,
    MemoryAdapter,
    DirectoryAdapter,
    IndexManager,
)


__all__ = [
    # Core indexing
    'IndexedText',
    'TextIndex',
    'create_indexed_text',
    
    # Serialization
    'Serializer',
    'JSONSerializer',
    'NDJSONSerializer',
    'CSVSerializer',
    'serialize',
    'deserialize',
    'save_to_file',
    'load_from_file',
    
    # Storage adapters
    'StorageAdapter',
    'FileAdapter',
    'MemoryAdapter',
    'DirectoryAdapter',
    'IndexManager',
]
