"""
Query module for Semantic Dropdown Search.

This module provides powerful querying capabilities over indexed texts
using semantic descriptors.
"""

from .predicates import (
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
    AlwaysTrue,
    AlwaysFalse,
    CustomPredicate,
)

from .filters import (
    Filter,
    filter_items,
    filter_index,
    find_by_domain,
    find_by_intent,
    find_research_posts,
    find_tutorials,
    find_by_author,
    find_recent,
    search_text,
)

from .query_builder import (
    QueryBuilder,
    QueryResult,
)

from .explain import (
    explain_query,
    explain_result,
    explain_predicate_tree,
    summarize_results,
    compare_queries,
    explain_why_matched,
    explain_why_not_matched,
    analyze_field_distribution,
    QueryExplainer,
)


__all__ = [
    # Predicates
    'Predicate',
    'FieldEquals',
    'FieldIn',
    'FieldStartsWith',
    'HierarchyMatches',
    'HierarchyDepth',
    'TextContains',
    'TextMatches',
    'MetadataEquals',
    'MetadataExists',
    'CreatedAfter',
    'CreatedBefore',
    'UpdatedAfter',
    'AndPredicate',
    'OrPredicate',
    'NotPredicate',
    'AlwaysTrue',
    'AlwaysFalse',
    'CustomPredicate',
    
    # Filters
    'Filter',
    'filter_items',
    'filter_index',
    'find_by_domain',
    'find_by_intent',
    'find_research_posts',
    'find_tutorials',
    'find_by_author',
    'find_recent',
    'search_text',
    
    # Query Builder
    'QueryBuilder',
    'QueryResult',
    
    # Explanation
    'explain_query',
    'explain_result',
    'explain_predicate_tree',
    'summarize_results',
    'compare_queries',
    'explain_why_matched',
    'explain_why_not_matched',
    'analyze_field_distribution',
    'QueryExplainer',
]
