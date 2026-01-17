"""
Query filters for Semantic Dropdown Search.

This module provides high-level filter helpers built on top of
predicate primitives.

Filters are convenience utilities, not a query language.
"""

from typing import List, Set, Optional, Dict, Any
from datetime import datetime

from ..indexer.index_text import IndexedText, TextIndex
from .predicates import (
    Predicate,
    FieldEquals,
    FieldIn,
    HierarchyMatches,
    TextContains,
    MetadataEquals,
    CreatedAfter,
    CreatedBefore,
    AndPredicate,
)


# -------------------------
# LOW-LEVEL HELPERS
# -------------------------

def filter_items(
    items: List[IndexedText],
    predicate: Predicate,
) -> List[IndexedText]:
    """Filter a list of items using a predicate."""
    return [item for item in items if predicate(item)]


def filter_index(
    index: TextIndex,
    predicate: Predicate,
) -> List[IndexedText]:
    """Filter a TextIndex using a predicate."""
    return filter_items(index.get_all(), predicate)


# -------------------------
# FILTER BUILDER
# -------------------------

class Filter:
    """
    Fluent filter builder for common query patterns.

    This is a thin convenience wrapper around predicates.
    """

    def __init__(self, items: Optional[List[IndexedText]] = None):
        self._items: List[IndexedText] = items or []
        self._predicates: List[Predicate] = []

    # ---- sources ----

    def with_items(self, items: List[IndexedText]) -> "Filter":
        self._items = items
        return self

    def from_index(self, index: TextIndex) -> "Filter":
        self._items = index.get_all()
        return self

    # ---- semantic fields ----

    def where_field(self, field_name: str, value: str) -> "Filter":
        self._predicates.append(FieldEquals(field_name, value))
        return self

    def where_field_in(self, field_name: str, values: Set[str]) -> "Filter":
        self._predicates.append(FieldIn(field_name, values))
        return self

    def where_domain(self, domain: str, exact: bool = False) -> "Filter":
        self._predicates.append(
            HierarchyMatches("domain", domain, exact)
        )
        return self

    def where_intent(self, intent: str, exact: bool = False) -> "Filter":
        self._predicates.append(
            HierarchyMatches("intent", intent, exact)
        )
        return self

    def where_tone(self, tone: str) -> "Filter":
        self._predicates.append(FieldEquals("tone", tone))
        return self

    def where_audience(self, audience: str) -> "Filter":
        self._predicates.append(FieldEquals("audience", audience))
        return self

    def where_stability(self, stability: str) -> "Filter":
        self._predicates.append(FieldEquals("stability", stability))
        return self

    # ---- text ----

    def where_text_contains(
        self,
        substring: str,
        case_sensitive: bool = False,
    ) -> "Filter":
        self._predicates.append(
            TextContains(substring, case_sensitive)
        )
        return self

    # ---- metadata ----

    def where_metadata(self, key: str, value: Any) -> "Filter":
        self._predicates.append(MetadataEquals(key, value))
        return self

    # ---- timestamps ----

    def where_created_after(self, timestamp: datetime) -> "Filter":
        self._predicates.append(CreatedAfter(timestamp))
        return self

    def where_created_before(self, timestamp: datetime) -> "Filter":
        self._predicates.append(CreatedBefore(timestamp))
        return self

    # ---- custom ----

    def where(self, predicate: Predicate) -> "Filter":
        self._predicates.append(predicate)
        return self

    # ---- execution ----

    def get_predicate(self) -> Optional[Predicate]:
        if not self._predicates:
            return None
        return AndPredicate(*self._predicates)

    def execute(self) -> List[IndexedText]:
        if not self._predicates:
            return self._items
        return filter_items(
            self._items,
            AndPredicate(*self._predicates),
        )

    def count(self) -> int:
        return len(self.execute())

    def first(self) -> Optional[IndexedText]:
        results = self.execute()
        return results[0] if results else None

    def exists(self) -> bool:
        return self.count() > 0

    def explain(self) -> str:
        predicate = self.get_predicate()
        return (
            "No filters applied"
            if predicate is None
            else predicate.explain()
        )


# -------------------------
# CONVENIENCE FUNCTIONS
# -------------------------

def find_by_domain(
    items: List[IndexedText],
    domain: str,
    exact: bool = False,
) -> List[IndexedText]:
    return Filter(items).where_domain(domain, exact).execute()


def find_by_intent(
    items: List[IndexedText],
    intent: str,
    exact: bool = False,
) -> List[IndexedText]:
    return Filter(items).where_intent(intent, exact).execute()


def find_research_posts(
    items: List[IndexedText],
    domain: Optional[str] = None,
    stability: Optional[str] = None,
) -> List[IndexedText]:
    f = Filter(items).where_intent("Research", exact=False)

    if domain:
        f.where_domain(domain, exact=False)
    if stability:
        f.where_stability(stability)

    return f.execute()


def find_tutorials(
    items: List[IndexedText],
    domain: Optional[str] = None,
) -> List[IndexedText]:
    f = Filter(items).where_intent("Documentation → Tutorial")

    if domain:
        f.where_domain(domain, exact=False)

    return f.execute()


def find_by_author(
    items: List[IndexedText],
    author: str,
) -> List[IndexedText]:
    return Filter(items).where_metadata("author", author).execute()


def find_recent(
    items: List[IndexedText],
    since: datetime,
) -> List[IndexedText]:
    return Filter(items).where_created_after(since).execute()


def search_text(
    items: List[IndexedText],
    query: str,
    case_sensitive: bool = False,
) -> List[IndexedText]:
    return Filter(items).where_text_contains(query, case_sensitive).execute()
