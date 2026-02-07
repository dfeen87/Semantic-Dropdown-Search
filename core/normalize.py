"""
Canonical normalization for Semantic Dropdown Search.

This module ensures semantic descriptors use consistent formatting,
making comparisons and indexing reliable.
"""

import re
from typing import Dict, Optional

from .errors import NormalizationError


# Canonical arrow separator for hierarchical paths
HIERARCHY_SEPARATOR = " → "

# Alternative separators users might input
ALTERNATIVE_SEPARATORS = [
    "->",
    "→",
    " > ",
    ">",
    "/",
    " / ",
    "|",
    " | ",
]


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.
    
    - Strips leading/trailing whitespace
    - Collapses multiple spaces to single space
    - Preserves hierarchy separators
    
    Args:
        text: Text to normalize
        
    Returns:
        Normalized text
    """
    # Protect hierarchy separators with flexible spacing around the arrow.
    protected = re.sub(r"\s*→\s*", "<<<HIERARCHY>>>", text)
    
    # Collapse whitespace
    normalized = re.sub(r'\s+', ' ', protected)
    
    # Strip leading/trailing
    normalized = normalized.strip()
    
    # Restore hierarchy separators
    normalized = normalized.replace("<<<HIERARCHY>>>", HIERARCHY_SEPARATOR)
    
    return normalized


def normalize_hierarchy_separator(text: str) -> str:
    """
    Normalize hierarchy separators to canonical form.
    
    Converts all alternative separators to the canonical HIERARCHY_SEPARATOR.
    
    Args:
        text: Text potentially containing hierarchy separators
        
    Returns:
        Text with normalized separators
    """
    result = text
    
    # Replace all alternative separators with canonical one
    for alt_sep in ALTERNATIVE_SEPARATORS:
        result = result.replace(alt_sep, HIERARCHY_SEPARATOR)
    
    return result


def normalize_case(text: str, preserve_case: bool = True) -> str:
    """
    Normalize text case.
    
    By default, preserves original case since semantic values
    may be case-sensitive (e.g., "DNA" vs "dna").
    
    Args:
        text: Text to normalize
        preserve_case: If True, preserve original case. If False, use title case.
        
    Returns:
        Normalized text
    """
    if preserve_case:
        return text
    
    # Title case, but preserve common acronyms
    # This is intentionally simple - schemas define canonical casing
    return text.title()


def normalize_field_name(field_name: str) -> str:
    """
    Normalize a field name to lowercase with underscores.
    
    This allows flexible field name input while maintaining consistency.
    
    Examples:
        "Domain" -> "domain"
        "Intent" -> "intent"
        "audience-type" -> "audience_type"
    
    Args:
        field_name: Field name to normalize
        
    Returns:
        Normalized field name
    """
    # Convert to lowercase
    normalized = field_name.lower()
    
    # Replace hyphens with underscores
    normalized = normalized.replace('-', '_')
    
    # Remove any whitespace
    normalized = normalized.replace(' ', '_')
    
    return normalized


def normalize_value(value: str, strict: bool = True) -> str:
    """
    Normalize a semantic value to canonical form.
    
    This is the primary normalization function for descriptor values.
    
    Steps:
    1. Normalize hierarchy separators
    2. Normalize whitespace
    3. Optionally preserve case (default: preserve)
    
    Args:
        value: Value to normalize
        strict: If True, raise error on empty result. If False, return empty string.
        
    Returns:
        Normalized value
        
    Raises:
        NormalizationError: If normalization produces empty string in strict mode
    """
    if not isinstance(value, str):
        raise NormalizationError(
            f"Value must be string, got {type(value).__name__}"
        )
    
    # Step 1: Normalize hierarchy separators
    result = normalize_hierarchy_separator(value)
    
    # Step 2: Normalize whitespace
    result = normalize_whitespace(result)
    
    # Step 3: Case preservation (schemas define canonical case)
    # We preserve case by default
    result = normalize_case(result, preserve_case=True)
    
    # Validate result
    if strict and not result:
        raise NormalizationError(
            f"Normalization produced empty string from input: '{value}'"
        )
    
    return result


def normalize_descriptor(descriptor: Dict[str, str], strict: bool = True) -> Dict[str, str]:
    """
    Normalize all fields and values in a semantic descriptor.
    
    Args:
        descriptor: Dictionary mapping field names to values
        strict: If True, raise errors on normalization issues
        
    Returns:
        New dictionary with normalized field names and values
        
    Raises:
        NormalizationError: If normalization fails in strict mode
    """
    if not isinstance(descriptor, dict):
        raise NormalizationError(
            f"Descriptor must be dict, got {type(descriptor).__name__}"
        )
    
    normalized = {}
    
    for field_name, value in descriptor.items():
        # Normalize field name
        norm_field = normalize_field_name(field_name)
        
        # Normalize value
        norm_value = normalize_value(value, strict=strict)
        
        # Check for duplicate fields after normalization
        if norm_field in normalized:
            if strict:
                raise NormalizationError(
                    f"Duplicate field after normalization: '{field_name}' and "
                    f"another field both normalize to '{norm_field}'"
                )
            else:
                # In non-strict mode, later values override
                pass
        
        normalized[norm_field] = norm_value
    
    return normalized


def are_values_equivalent(value1: str, value2: str) -> bool:
    """
    Check if two values are semantically equivalent after normalization.
    
    This is useful for comparing user input against schema values.
    
    Args:
        value1: First value
        value2: Second value
        
    Returns:
        True if values are equivalent after normalization
    """
    try:
        norm1 = normalize_value(value1, strict=False)
        norm2 = normalize_value(value2, strict=False)
        return norm1 == norm2
    except NormalizationError:
        return False


def get_hierarchy_path(value: str) -> list:
    """
    Extract hierarchy path from a normalized value.
    
    Example:
        "Science → Biology → Systems Biology" 
        -> ["Science", "Biology", "Systems Biology"]
    
    Args:
        value: Normalized hierarchical value
        
    Returns:
        List of path components
    """
    if HIERARCHY_SEPARATOR not in value:
        return [value]
    
    return [part.strip() for part in value.split(HIERARCHY_SEPARATOR)]


def get_hierarchy_depth(value: str) -> int:
    """
    Get the depth of a hierarchical value.
    
    Examples:
        "Science" -> 1
        "Science → Biology" -> 2
        "Science → Biology → Systems Biology" -> 3
    
    Args:
        value: Normalized hierarchical value
        
    Returns:
        Depth of hierarchy (1 for non-hierarchical)
    """
    return len(get_hierarchy_path(value))


def is_hierarchical(value: str) -> bool:
    """
    Check if a value is hierarchical.
    
    Args:
        value: Value to check
        
    Returns:
        True if value contains hierarchy separator
    """
    return HIERARCHY_SEPARATOR in value


def get_parent_value(value: str) -> Optional[str]:
    """
    Get the parent value in a hierarchy.
    
    Example:
        "Science → Biology → Systems Biology" -> "Science → Biology"
        "Science → Biology" -> "Science"
        "Science" -> None
    
    Args:
        value: Hierarchical value
        
    Returns:
        Parent value, or None if at root level
    """
    if not is_hierarchical(value):
        return None
    
    path = get_hierarchy_path(value)
    if len(path) <= 1:
        return None
    
    return HIERARCHY_SEPARATOR.join(path[:-1])


def get_root_value(value: str) -> str:
    """
    Get the root value in a hierarchy.
    
    Example:
        "Science → Biology → Systems Biology" -> "Science"
        "Science → Biology" -> "Science"
        "Science" -> "Science"
    
    Args:
        value: Hierarchical value
        
    Returns:
        Root value
    """
    path = get_hierarchy_path(value)
    return path[0]
