"""
Query explanation for Semantic Dropdown Search.

This module provides human-readable explanations of queries and query results.
"""

from typing import List, Dict, Any, Optional
from collections import Counter

from indexer import IndexedText
from .predicates import Predicate
from .query_builder import QueryResult


def explain_query(predicate: Optional[Predicate],
                 limit: Optional[int] = None,
                 offset: int = 0,
                 sort_key: Optional[str] = None,
                 sort_reverse: bool = False) -> str:
    """
    Generate human-readable query explanation.
    """
    parts = []

    # Predicate explanation
    if predicate:
        parts.append(f"Select items where {predicate.explain()}")
    else:
        parts.append("Select all items")

    # Sorting
    if sort_key:
        direction = "descending" if sort_reverse else "ascending"
        parts.append(f"sorted by {sort_key} ({direction})")

    # Pagination
    if offset > 0 and limit:
        parts.append(f"showing results {offset + 1} to {offset + limit}")
    elif offset > 0:
        parts.append(f"skipping first {offset} results")
    elif limit:
        parts.append(f"limited to {limit} results")

    return ", ".join(parts) + "."


def explain_result(result: QueryResult, verbose: bool = False) -> str:
    """
    Generate human-readable explanation of query result.
    """
    explanation = []

    explanation.append(f"Query: {result.query_explanation}")
    explanation.append(f"\nFound {result.total} matching items")

    if len(result.items) < result.total:
        explanation.append(f" (showing {len(result.items)})")

    if verbose and result.items:
        explanation.append("\n\nField Distribution:")

        field_stats = analyze_field_distribution(result.items)
        for field_name, values in field_stats.items():
            explanation.append(f"\n  {field_name}:")
            for value, count in values.most_common(5):
                percentage = (count / len(result.items)) * 100
                explanation.append(f"    • {value}: {count} ({percentage:.1f}%)")

    return "".join(explanation)


def analyze_field_distribution(items: List[IndexedText]) -> Dict[str, Counter]:
    """
    Analyze distribution of field values in items.
    """
    fields = ['domain', 'intent', 'tone', 'audience', 'stability']
    distribution = {}

    for field_name in fields:
        counter = Counter()
        for item in items:
            value = item.descriptor.get_field(field_name)
            if value:
                counter[value] += 1

        if counter:
            distribution[field_name] = counter

    return distribution


def explain_predicate_tree(predicate: Predicate, indent: int = 0) -> str:
    """
    Generate tree visualization of predicate structure.
    """
    from .predicates import AndPredicate, OrPredicate, NotPredicate

    prefix = "  " * indent

    if isinstance(predicate, AndPredicate):
        lines = [f"{prefix}AND:"]
        for p in predicate.predicates:
            lines.append(explain_predicate_tree(p, indent + 1))
        return "\n".join(lines)

    elif isinstance(predicate, OrPredicate):
        lines = [f"{prefix}OR:"]
        for p in predicate.predicates:
            lines.append(explain_predicate_tree(p, indent + 1))
        return "\n".join(lines)

    elif isinstance(predicate, NotPredicate):
        lines = [f"{prefix}NOT:"]
        lines.append(explain_predicate_tree(predicate.predicate, indent + 1))
        return "\n".join(lines)

    else:
        return f"{prefix}• {predicate.explain()}"


def summarize_results(items: List[IndexedText], max_items: int = 10) -> str:
    """
    Generate summary of results.
    """
    if not items:
        return "No items found."

    lines = [f"Found {len(items)} items:\n"]

    for i, item in enumerate(items[:max_items], 1):
        text_preview = item.text[:60] + "..." if len(item.text) > 60 else item.text
        lines.append(f"{i}. {text_preview}")

        descriptor_parts = []
        if item.descriptor.domain:
            descriptor_parts.append(f"domain: {item.descriptor.domain}")
        if item.descriptor.intent:
            descriptor_parts.append(f"intent: {item.descriptor.intent}")

        if descriptor_parts:
            lines.append(f"   [{', '.join(descriptor_parts)}]")

        lines.append("")

    if len(items) > max_items:
        lines.append(f"... and {len(items) - max_items} more items")

    return "\n".join(lines)


def compare_queries(result1: QueryResult, result2: QueryResult) -> str:
    """
    Compare two query results.
    """
    lines = [
        "Query Comparison:\n",
        "Query 1:",
        f"  {result1.query_explanation}",
        f"  Results: {result1.total} items\n",
        "Query 2:",
        f"  {result2.query_explanation}",
        f"  Results: {result2.total} items\n",
    ]

    ids1 = {item.id for item in result1.items}
    ids2 = {item.id for item in result2.items}

    lines.extend([
        "Overlap:",
        f"  Common items: {len(ids1 & ids2)}",
        f"  Only in Query 1: {len(ids1 - ids2)}",
        f"  Only in Query 2: {len(ids2 - ids1)}",
    ])

    return "\n".join(lines)


def explain_why_matched(item: IndexedText, predicate: Optional[Predicate]) -> str:
    """
    Explain why an item matched a predicate.
    """
    if predicate is None:
        return f"Item {item.id} matched because no filter was applied."

    from .predicates import AndPredicate, OrPredicate, FieldEquals, HierarchyMatches, TextContains

    lines = [f"Item {item.id} matched because:\n"]

    def explain_match(pred: Predicate, level: int = 0) -> List[str]:
        indent = "  " * level
        result = []

        if isinstance(pred, AndPredicate):
            result.append(f"{indent}All of the following were true:")
            for p in pred.predicates:
                result.extend(explain_match(p, level + 1))

        elif isinstance(pred, OrPredicate):
            result.append(f"{indent}At least one of the following was true:")
            for p in pred.predicates:
                if p.test(item):
                    result.extend(explain_match(p, level + 1))
                    break

        elif isinstance(pred, FieldEquals):
            value = item.descriptor.get_field(pred.field_name)
            result.append(f"{indent}• {pred.field_name} = '{value}'")

        elif isinstance(pred, HierarchyMatches):
            value = item.descriptor.get_field(pred.field_name)
            result.append(f"{indent}• {pred.field_name} = '{value}' (hierarchy match)")

        elif isinstance(pred, TextContains):
            result.append(f"{indent}• text contains '{pred.substring}'")

        else:
            result.append(f"{indent}• {pred.explain()}")

        return result

    lines.extend(explain_match(predicate))
    return "\n".join(lines)


def explain_why_not_matched(item: IndexedText, predicate: Optional[Predicate]) -> str:
    """
    Explain why an item did NOT match a predicate.
    """
    if predicate is None:
        return f"Item {item.id} was excluded because no filter was applied."

    from .predicates import AndPredicate, OrPredicate, FieldEquals, HierarchyMatches

    lines = [f"Item {item.id} did NOT match because:\n"]

    def explain_non_match(pred: Predicate, level: int = 0) -> List[str]:
        indent = "  " * level
        result = []

        if isinstance(pred, AndPredicate):
            failed = [p for p in pred.predicates if not p.test(item)]
            result.append(f"{indent}The following conditions failed:")
            for p in failed:
                result.extend(explain_non_match(p, level + 1))

        elif isinstance(pred, OrPredicate):
            result.append(f"{indent}None of the following were true:")
            for p in pred.predicates:
                result.extend(explain_non_match(p, level + 1))

        elif isinstance(pred, FieldEquals):
            value = item.descriptor.get_field(pred.field_name)
            result.append(
                f"{indent}• {pred.field_name} = '{value}' (expected '{pred.value}')"
            )

        elif isinstance(pred, HierarchyMatches):
            value = item.descriptor.get_field(pred.field_name)
            result.append(
                f"{indent}• {pred.field_name} = '{value}' (expected under '{pred.path}')"
            )

        else:
            result.append(f"{indent}• {pred.explain()} was false")

        return result

    lines.extend(explain_non_match(predicate))
    return "\n".join(lines)


class QueryExplainer:
    """
    Helper class for explaining queries interactively.
    """

    def __init__(self, result: QueryResult):
        self.result = result

    def summary(self) -> str:
        return explain_result(self.result, verbose=False)

    def detailed(self) -> str:
        return explain_result(self.result, verbose=True)

    def items(self, max_items: int = 10) -> str:
        return summarize_results(self.result.items, max_items)

    def statistics(self) -> Dict[str, Any]:
        stats = {
            'total': self.result.total,
            'returned': len(self.result.items),
            'query': self.result.query_explanation,
        }

        if self.result.items:
            stats['field_distribution'] = analyze_field_distribution(self.result.items)

        return stats

    def __str__(self) -> str:
        return self.summary()
