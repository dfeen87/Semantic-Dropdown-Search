"""
Core module for Semantic Dropdown Search.

This module provides the fundamental building blocks:
- SemanticDescriptor: The main descriptor object
- Validation: Schema validation against dropdown definitions
- Normalization: Canonical formatting for consistency
- Errors: Custom exceptions
"""

from .descriptor import SemanticDescriptor
from .validate import (
    SchemaValidator,
    ValidationResult,
    validate,
)
from .normalize import (
    normalize_descriptor,
    normalize_value,
    normalize_field_name,
    are_values_equivalent,
    get_hierarchy_path,
    get_hierarchy_depth,
    is_hierarchical,
    get_parent_value,
    get_root_value,
    HIERARCHY_SEPARATOR,
)
from .errors import (
    SemanticDropdownError,
    ValidationError,
    SchemaError,
    SchemaVersionError,
    NormalizationError,
    IndexingError,
    QueryError,
)


__all__ = [
    # Main descriptor class
    'SemanticDescriptor',
    
    # Validation
    'SchemaValidator',
    'ValidationResult',
    'validate',
    
    # Normalization
    'normalize_descriptor',
    'normalize_value',
    'normalize_field_name',
    'are_values_equivalent',
    'get_hierarchy_path',
    'get_hierarchy_depth',
    'is_hierarchical',
    'get_parent_value',
    'get_root_value',
    'HIERARCHY_SEPARATOR',
    
    # Errors
    'SemanticDropdownError',
    'ValidationError',
    'SchemaError',
    'SchemaVersionError',
    'NormalizationError',
    'IndexingError',
    'QueryError',
]


# Version info
__version__ = '1.0.0'
