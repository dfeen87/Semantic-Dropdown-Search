"""
Query builder for Semantic Dropdown Search.

This module provides a fluent API for constructing complex queries
over indexed text content.

This is an advanced interface built on top of predicates.
Most users should prefer `filters.py`.
"""

from typing import List, Optional, Set, Any, Callable
from datetime import datetime
from dataclasses import dataclass

from indexer.index_text import IndexedText, TextIndex
from query.predicates import (
    Predicate,
    FieldEquals,
    FieldIn,
    FieldStartsWith,
    HierarchyMatches,
    HierarchyDepth,
    TextContains,
    TextMatches,
    MetadataEquals,
    MetadataExists,
    CreatedAfter,
    CreatedBefore,
    UpdatedAfter,
    AndPredicate,
    OrPredicate,
    NotPredicate,
    CustomPredicate,
)
from core.errors import QueryError


# -------------------------
# QUERY RESULT
# -------------------------

@dataclass
class QueryResult:
    """Result of query execution."""
    items: List[IndexedText]
    total: int
    query_explanation: str

    def __len__(self):
        return self.total

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, index):
        return self.items[index]


# -------------------------
# QUERY BUILDER
# -------------------------

class QueryBuilder:
    """
    Fluent query builder for indexed texts.

    This is a convenience wrapper around predicates,
    not a full query language.
    """

    def __init__(self, index: Optional[TextIndex] = None):
        self._index = index
        self._predicates: List[Predicate] = []

        self._limit: Optional[int] = None
        self._offset: int = 0

        self._sort_key: Optional[Callable[[IndexedText], Any]] = None
        self._sort_reverse: bool = False

    # ---------------------
    # SOURCE
    # ---------------------

    def from_index(self, index: TextIndex) -> "QueryBuilder":
        self._index = index
        return self

    # ---------------------
    # FIELD MATCHING
    # ---------------------

    def where_field(self, field_name: str, value: str) -> "QueryBuilder":
        self._predicates.append(FieldEquals(field_name, value))
        return self

    def where_field_in(self, field_name: str, values: Set[str]) -> "QueryBuilder":
        self._predicates.append(FieldIn(field_name, values))
        return self

    def where_field_starts_with(self, field_name: str, prefix: str) -> "QueryBuilder":
        self._predicates.append(FieldStartsWith(field_name, prefix))
        return self

    # ---------------------
    # HIERARCHY
    # ---------------------

    def where_hierarchy(self, field_name: str, path: str, exact: bool = False) -> "QueryBuilder":
        self._predicates.append(HierarchyMatches(field_name, path, exact))
        return self

    def where_hierarchy_depth(
        self,
        field_name: str,
        min_depth: Optional[int] = None,
        max_depth: Optional[int] = None,
    ) -> "QueryBuilder":
        self._predicates.append(
            HierarchyDepth(field_name, min_depth, max_depth)
        )
        return self

    # ---------------------
    # SHORTCUTS
    # ---------------------

    def where_domain(self, domain: str, exact: bool = False) -> "QueryBuilder":
        return self.where_hierarchy("domain", domain, exact)

    def where_intent(self, intent: str, exact: bool = False) -> "QueryBuilder":
        return self.where_hierarchy("intent", intent, exact)

    def where_tone(self, tone: str) -> "QueryBuilder":
        return self.where_field("tone", tone)

    def where_audience(self, audience: str) -> "QueryBuilder":
        return self.where_field("audience", audience)

    def where_stability(self, stability: str) -> "QueryBuilder":
        return self.where_field("stability", stability)

    # ---------------------
    # TEXT
    # ---------------------

    def where_text_contains(self, substring: str, case_sensitive: bool = False) -> "QueryBuilder":
        self._predicates.append(TextContains(substring, case_sensitive))
        return self

    def where_text_matches(
        self,
        matcher: Callable[[str], bool],
        description: str,
    ) -> "QueryBuilder":
        self._predicates.append(TextMatches(matcher, description))
        return self

    # ---------------------
    # METADATA
    # ---------------------

    def where_metadata(self, key: str, value: Any) -> "QueryBuilder":
        self._predicates.append(MetadataEquals(key, value))
        return self

    def where_metadata_exists(self, key: str) -> "QueryBuilder":
        self._predicates.append(MetadataExists(key))
        return self

    # ---------------------
    # TIMESTAMPS
    # ---------------------

    def where_created_after(self, timestamp: datetime) -> "QueryBuilder":
        self._predicates.append(CreatedAfter(timestamp))
        return self

    def where_created_before(self, timestamp: datetime) -> "QueryBuilder":
        self._predicates.append(CreatedBefore(timestamp))
        return self

    def where_updated_after(self, timestamp: datetime) -> "QueryBuilder":
        self._predicates.append(UpdatedAfter(timestamp))
        return self

    # ---------------------
    # CUSTOM / LOGICAL
    # ---------------------

    def where(self, predicate: Predicate) -> "QueryBuilder":
        self._predicates.append(predicate)
        return self

    def or_where(self, *predicates: Predicate) -> "QueryBuilder":
        if predicates:
            self._predicates.append(OrPredicate(*predicates))
        return self

    def not_where(self, predicate: Predicate) -> "QueryBuilder":
        self._predicates.append(NotPredicate(predicate))
        return self

    # ---------------------
    # SORTING / PAGINATION
    # ---------------------

    def order_by(
        self,
        key: Callable[[IndexedText], Any],
        reverse: bool = False,
    ) -> "QueryBuilder":
        self._sort_key = key
        self._sort_reverse = reverse
        return self

    def order_by_created(self, descending: bool = True) -> "QueryBuilder":
        return self.order_by(lambda item: item.created_at, reverse=descending)

    def order_by_updated(self, descending: bool = True) -> "QueryBuilder":
        return self.order_by(lambda item: item.updated_at, reverse=descending)

    def limit(self, n: int) -> "QueryBuilder":
        self._limit = n
        return self

    def offset(self, n: int) -> "QueryBuilder":
        self._offset = n
        return self

    # ---------------------
    # UTILITIES
    # ---------------------

    def clone(self) -> "QueryBuilder":
        """Create a shallow copy of the current query builder."""
        cloned = QueryBuilder(self._index)
        cloned._predicates = list(self._predicates)
        cloned._limit = self._limit
        cloned._offset = self._offset
        cloned._sort_key = self._sort_key
        cloned._sort_reverse = self._sort_reverse
        return cloned

    def reset(self) -> "QueryBuilder":
        """Reset predicates, sorting, and pagination."""
        self._predicates = []
        self._limit = None
        self._offset = 0
        self._sort_key = None
        self._sort_reverse = False
        return self

    def count(self) -> int:
        """Return the number of items matching the query."""
        return len(self.execute().items)

    def first(self) -> Optional[IndexedText]:
        """Return the first matching item, if any."""
        results = self.execute().items
        return results[0] if results else None

    def exists(self) -> bool:
        """Return True if any items match the query."""
        return self.count() > 0

    # ---------------------
    # EXECUTION
    # ---------------------

    def build_predicate(self) -> Optional[Predicate]:
        if not self._predicates:
            return None
        if len(self._predicates) == 1:
            return self._predicates[0]
        return AndPredicate(*self._predicates)

    def execute(self) -> QueryResult:
        if self._index is None:
            raise QueryError("No index set. Use from_index() first.")

        items = self._index.get_all()
        predicate = self.build_predicate()

        if predicate:
            items = [item for item in items if predicate(item)]

        total = len(items)

        if self._sort_key:
            items.sort(key=self._sort_key, reverse=self._sort_reverse)

        if self._offset:
            items = items[self._offset:]

        if self._limit is not None:
            items = items[: self._limit]

        return QueryResult(
            items=items,
            total=total,
            query_explanation=self.explain(),
        )

    def explain(self) -> str:
        predicate = self.build_predicate()
        parts = []

        if predicate:
            parts.append(f"WHERE {predicate.explain()}")
        if self._sort_key:
            parts.append("ORDER BY")
        if self._offset:
            parts.append(f"OFFSET {self._offset}")
        if self._limit is not None:
            parts.append(f"LIMIT {self._limit}")

        return "SELECT items " + " ".join(parts) if parts else "SELECT all items"
