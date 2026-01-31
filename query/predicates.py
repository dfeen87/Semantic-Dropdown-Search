"""
Query predicates for Semantic Dropdown Search.

This module defines predicates for matching indexed texts based on
their semantic descriptors, text content, metadata, and timestamps.

Predicates are pure boolean filters.
They perform no ranking, scoring, or inference.
"""

from typing import Callable, Set, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime

from ..indexer.index_text import IndexedText
from ..core.normalize import (
    HIERARCHY_SEPARATOR,
    get_hierarchy_path,
    get_hierarchy_depth,
)


# -------------------------
# BASE PREDICATE
# -------------------------

class Predicate(ABC):
    """Abstract base class for query predicates."""

    @abstractmethod
    def test(self, item: IndexedText) -> bool:
        """Return True if item matches predicate."""
        pass

    @abstractmethod
    def explain(self) -> str:
        """Return human-readable explanation."""
        pass

    def __call__(self, item: IndexedText) -> bool:
        return self.test(item)

    def __and__(self, other: "Predicate") -> "AndPredicate":
        return AndPredicate(self, other)

    def __or__(self, other: "Predicate") -> "OrPredicate":
        return OrPredicate(self, other)

    def __invert__(self) -> "NotPredicate":
        return NotPredicate(self)


# -------------------------
# FIELD-BASED PREDICATES
# -------------------------

class FieldEquals(Predicate):
    """Match items where a semantic field equals a value."""

    def __init__(self, field_name: str, value: str):
        self.field_name = field_name
        self.value = value

    def test(self, item: IndexedText) -> bool:
        return item.descriptor.get_field(self.field_name) == self.value

    def explain(self) -> str:
        return f"{self.field_name} = '{self.value}'"


class FieldIn(Predicate):
    """Match items where a semantic field is in a set of values."""

    def __init__(self, field_name: str, values: Set[str]):
        self.field_name = field_name
        self.values = values

    def test(self, item: IndexedText) -> bool:
        return item.descriptor.get_field(self.field_name) in self.values

    def explain(self) -> str:
        vals = ", ".join(f"'{v}'" for v in sorted(self.values))
        return f"{self.field_name} in [{vals}]"


class FieldStartsWith(Predicate):
    """Match items where a semantic field starts with a prefix."""

    def __init__(self, field_name: str, prefix: str):
        self.field_name = field_name
        self.prefix = prefix

    def test(self, item: IndexedText) -> bool:
        value = item.descriptor.get_field(self.field_name)
        return value is not None and value.startswith(self.prefix)

    def explain(self) -> str:
        return f"{self.field_name} starts with '{self.prefix}'"


# -------------------------
# HIERARCHY PREDICATES
# -------------------------

class HierarchyMatches(Predicate):
    """
    Match items where a hierarchical field matches or is a descendant
    of a given path.
    """

    def __init__(self, field_name: str, path: str, exact: bool = False):
        self.field_name = field_name
        self.path = path
        self.exact = exact

    def test(self, item: IndexedText) -> bool:
        value = item.descriptor.get_field(self.field_name)
        if value is None:
            return False

        if self.exact:
            return value == self.path

        return value == self.path or value.startswith(f"{self.path}{HIERARCHY_SEPARATOR}")

    def explain(self) -> str:
        return (
            f"{self.field_name} = '{self.path}'"
            if self.exact
            else f"{self.field_name} under '{self.path}'"
        )


class HierarchyDepth(Predicate):
    """Match items based on hierarchy depth."""

    def __init__(
        self,
        field_name: str,
        min_depth: Optional[int] = None,
        max_depth: Optional[int] = None,
    ):
        self.field_name = field_name
        self.min_depth = min_depth
        self.max_depth = max_depth

    def test(self, item: IndexedText) -> bool:
        value = item.descriptor.get_field(self.field_name)
        if value is None:
            return False

        depth = get_hierarchy_depth(value)

        if self.min_depth is not None and depth < self.min_depth:
            return False
        if self.max_depth is not None and depth > self.max_depth:
            return False

        return True

    def explain(self) -> str:
        parts = []
        if self.min_depth is not None:
            parts.append(f"depth ≥ {self.min_depth}")
        if self.max_depth is not None:
            parts.append(f"depth ≤ {self.max_depth}")
        return f"{self.field_name} ({' and '.join(parts)})"


# -------------------------
# TEXT PREDICATES
# -------------------------

class TextContains(Predicate):
    """Match items where text contains a substring."""

    def __init__(self, substring: str, case_sensitive: bool = False):
        self.substring = substring
        self.case_sensitive = case_sensitive

    def test(self, item: IndexedText) -> bool:
        text = item.text
        needle = self.substring

        if not self.case_sensitive:
            text = text.lower()
            needle = needle.lower()

        return needle in text

    def explain(self) -> str:
        mode = "case-sensitive" if self.case_sensitive else "case-insensitive"
        return f"text contains '{self.substring}' ({mode})"


class TextMatches(Predicate):
    """Match items using a custom text matcher function."""

    def __init__(self, matcher: Callable[[str], bool], description: str):
        self.matcher = matcher
        self.description = description

    def test(self, item: IndexedText) -> bool:
        return self.matcher(item.text)

    def explain(self) -> str:
        return f"text {self.description}"


# -------------------------
# METADATA PREDICATES
# -------------------------

class MetadataEquals(Predicate):
    """Match items where a metadata key equals a value."""

    def __init__(self, key: str, value: Any):
        self.key = key
        self.value = value

    def test(self, item: IndexedText) -> bool:
        return item.metadata.get(self.key) == self.value

    def explain(self) -> str:
        return f"metadata['{self.key}'] = {self.value!r}"


class MetadataExists(Predicate):
    """Match items where a metadata key exists."""

    def __init__(self, key: str):
        self.key = key

    def test(self, item: IndexedText) -> bool:
        return self.key in item.metadata

    def explain(self) -> str:
        return f"metadata['{self.key}'] exists"


# -------------------------
# TIME PREDICATES
# -------------------------

class CreatedAfter(Predicate):
    """Match items created after a timestamp."""

    def __init__(self, timestamp: datetime):
        self.timestamp = timestamp

    def test(self, item: IndexedText) -> bool:
        return item.created_at > self.timestamp

    def explain(self) -> str:
        return f"created after {self.timestamp.isoformat()}"


class CreatedBefore(Predicate):
    """Match items created before a timestamp."""

    def __init__(self, timestamp: datetime):
        self.timestamp = timestamp

    def test(self, item: IndexedText) -> bool:
        return item.created_at < self.timestamp

    def explain(self) -> str:
        return f"created before {self.timestamp.isoformat()}"


class UpdatedAfter(Predicate):
    """Match items updated after a timestamp."""

    def __init__(self, timestamp: datetime):
        self.timestamp = timestamp

    def test(self, item: IndexedText) -> bool:
        return item.updated_at > self.timestamp

    def explain(self) -> str:
        return f"updated after {self.timestamp.isoformat()}"


# -------------------------
# LOGICAL COMBINATORS
# -------------------------

class AndPredicate(Predicate):
    """Combine predicates using AND logic."""

    def __init__(self, *predicates: Predicate):
        self.predicates = predicates

    def test(self, item: IndexedText) -> bool:
        return all(p.test(item) for p in self.predicates)

    def explain(self) -> str:
        return "(" + " AND ".join(p.explain() for p in self.predicates) + ")"


class OrPredicate(Predicate):
    """Combine predicates using OR logic."""

    def __init__(self, *predicates: Predicate):
        self.predicates = predicates

    def test(self, item: IndexedText) -> bool:
        return any(p.test(item) for p in self.predicates)

    def explain(self) -> str:
        return "(" + " OR ".join(p.explain() for p in self.predicates) + ")"


class NotPredicate(Predicate):
    """Negate a predicate."""

    def __init__(self, predicate: Predicate):
        self.predicate = predicate

    def test(self, item: IndexedText) -> bool:
        return not self.predicate.test(item)

    def explain(self) -> str:
        return f"NOT ({self.predicate.explain()})"


# -------------------------
# CONSTANT PREDICATES
# -------------------------

class AlwaysTrue(Predicate):
    """Predicate that always matches."""

    def test(self, item: IndexedText) -> bool:
        return True

    def explain(self) -> str:
        return "always true"


class AlwaysFalse(Predicate):
    """Predicate that never matches."""

    def test(self, item: IndexedText) -> bool:
        return False

    def explain(self) -> str:
        return "always false"


class CustomPredicate(Predicate):
    """Predicate backed by a custom test function."""

    def __init__(
        self,
        test_func: Callable[[IndexedText], bool],
        description: str,
    ):
        self.test_func = test_func
        self.description = description

    def test(self, item: IndexedText) -> bool:
        return self.test_func(item)

    def explain(self) -> str:
        return self.description
