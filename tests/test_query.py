"""
Tests for query functionality.
"""

import unittest
from datetime import datetime, timedelta, timezone

from core import SemanticDescriptor
from indexer import TextIndex, IndexedText
from query import (
    QueryBuilder,
    Filter,
    FieldEquals,
    HierarchyMatches,
    TextContains,
    AndPredicate,
    OrPredicate,
    NotPredicate,
    find_research_posts,
    find_tutorials,
)


class TestPredicates(unittest.TestCase):
    """Test predicate functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.descriptor = SemanticDescriptor(
            domain='Science → Biology',
            intent='Research → Conceptual',
            tone='Analytical',
            audience='Researchers'
        )
        
        self.index = TextIndex()
        self.item = self.index.add(
            'Test research text',
            self.descriptor,
            metadata={'author': 'Dr. Smith'}
        )
    
    def test_field_equals_predicate(self):
        """Test FieldEquals predicate."""
        predicate = FieldEquals('tone', 'Analytical')
        self.assertTrue(predicate.test(self.item))
        
        predicate_false = FieldEquals('tone', 'Formal')
        self.assertFalse(predicate_false.test(self.item))
    
    def test_hierarchy_matches_exact(self):
        """Test HierarchyMatches with exact match."""
        predicate = HierarchyMatches('domain', 'Science → Biology', exact=True)
        self.assertTrue(predicate.test(self.item))
        
        predicate_false = HierarchyMatches('domain', 'Science', exact=True)
        self.assertFalse(predicate_false.test(self.item))
    
    def test_hierarchy_matches_descendant(self):
        """Test HierarchyMatches with descendant matching."""
        predicate = HierarchyMatches('domain', 'Science', exact=False)
        self.assertTrue(predicate.test(self.item))
        
        predicate = HierarchyMatches('domain', 'Science → Biology', exact=False)
        self.assertTrue(predicate.test(self.item))
    
    def test_text_contains_predicate(self):
        """Test TextContains predicate."""
        predicate = TextContains('research', case_sensitive=False)
        self.assertTrue(predicate.test(self.item))
        
        predicate_false = TextContains('tutorial', case_sensitive=False)
        self.assertFalse(predicate_false.test(self.item))
    
    def test_and_predicate(self):
        """Test AND logic."""
        pred1 = FieldEquals('tone', 'Analytical')
        pred2 = HierarchyMatches('domain', 'Science', exact=False)
        
        combined = AndPredicate(pred1, pred2)
        self.assertTrue(combined.test(self.item))
        
        pred3 = FieldEquals('tone', 'Formal')
        combined_false = AndPredicate(pred1, pred3)
        self.assertFalse(combined_false.test(self.item))
    
    def test_or_predicate(self):
        """Test OR logic."""
        pred1 = FieldEquals('tone', 'Analytical')
        pred2 = FieldEquals('tone', 'Formal')
        
        combined = OrPredicate(pred1, pred2)
        self.assertTrue(combined.test(self.item))
        
        pred3 = FieldEquals('tone', 'Casual')
        combined_false = OrPredicate(pred2, pred3)
        self.assertFalse(combined_false.test(self.item))
    
    def test_not_predicate(self):
        """Test NOT logic."""
        pred = FieldEquals('tone', 'Formal')
        negated = NotPredicate(pred)
        
        self.assertTrue(negated.test(self.item))
    
    def test_predicate_operators(self):
        """Test predicate operators (&, |, ~)."""
        pred1 = FieldEquals('tone', 'Analytical')
        pred2 = HierarchyMatches('domain', 'Science', exact=False)
        
        # AND operator
        combined_and = pred1 & pred2
        self.assertTrue(combined_and.test(self.item))
        
        # OR operator
        pred3 = FieldEquals('tone', 'Formal')
        combined_or = pred1 | pred3
        self.assertTrue(combined_or.test(self.item))
        
        # NOT operator
        negated = ~pred3
        self.assertTrue(negated.test(self.item))
    
    def test_predicate_explain(self):
        """Test predicate explanation."""
        predicate = FieldEquals('domain', 'Science')
        explanation = predicate.explain()
        
        self.assertIn('domain', explanation)
        self.assertIn('Science', explanation)


class TestQueryBuilder(unittest.TestCase):
    """Test QueryBuilder functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.index = TextIndex()
        
        # Add test items
        self.index.add(
            'Biology research text',
            SemanticDescriptor(
                domain='Science → Biology',
                intent='Research → Conceptual'
            )
        )
        
        self.index.add(
            'Physics research text',
            SemanticDescriptor(
                domain='Science → Physics',
                intent='Research → Applied'
            )
        )
        
        self.index.add(
            'Python tutorial',
            SemanticDescriptor(
                domain='Engineering → Software Engineering',
                intent='Documentation → Tutorial',
                audience='Beginners'
            )
        )
    
    def test_basic_query(self):
        """Test basic query."""
        result = (QueryBuilder(self.index)
                 .where_domain('Science', exact=False)
                 .execute())
        
        self.assertEqual(len(result.items), 2)
        self.assertEqual(result.total, 2)
    
    def test_exact_match_query(self):
        """Test exact match query."""
        result = (QueryBuilder(self.index)
                 .where_domain('Science → Biology', exact=True)
                 .execute())
        
        self.assertEqual(len(result.items), 1)
    
    def test_multiple_filters(self):
        """Test query with multiple filters."""
        result = (QueryBuilder(self.index)
                 .where_domain('Science', exact=False)
                 .where_intent('Research → Conceptual')
                 .execute())
        
        self.assertEqual(len(result.items), 1)
    
    def test_text_search(self):
        """Test text search."""
        result = (QueryBuilder(self.index)
                 .where_text_contains('tutorial', case_sensitive=False)
                 .execute())
        
        self.assertEqual(len(result.items), 1)
    
    def test_or_query(self):
        """Test OR query."""
        bio = HierarchyMatches('domain', 'Science → Biology')
        physics = HierarchyMatches('domain', 'Science → Physics')
        
        result = (QueryBuilder(self.index)
                 .or_where(bio, physics)
                 .execute())
        
        self.assertEqual(len(result.items), 2)
    
    def test_limit(self):
        """Test result limiting."""
        result = (QueryBuilder(self.index)
                 .where_domain('Science', exact=False)
                 .limit(1)
                 .execute())
        
        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.total, 2)  # Total before limit
    
    def test_offset(self):
        """Test result offset."""
        result = (QueryBuilder(self.index)
                 .where_domain('Science', exact=False)
                 .offset(1)
                 .execute())
        
        self.assertEqual(len(result.items), 1)
    
    def test_sorting_by_created(self):
        """Test sorting by creation date."""
        result = (QueryBuilder(self.index)
                 .order_by_created(descending=True)
                 .execute())
        
        # Items should be in reverse chronological order
        timestamps = [item.created_at for item in result.items]
        self.assertEqual(timestamps, sorted(timestamps, reverse=True))
    
    def test_count(self):
        """Test count method."""
        count = (QueryBuilder(self.index)
                .where_domain('Science', exact=False)
                .count())
        
        self.assertEqual(count, 2)
    
    def test_first(self):
        """Test first method."""
        item = (QueryBuilder(self.index)
               .where_domain('Science → Biology')
               .first())
        
        self.assertIsNotNone(item)
        self.assertEqual(item.descriptor.domain, 'Science → Biology')
    
    def test_exists(self):
        """Test exists method."""
        exists = (QueryBuilder(self.index)
                 .where_domain('Science', exact=False)
                 .exists())
        
        self.assertTrue(exists)
        
        not_exists = (QueryBuilder(self.index)
                     .where_domain('NonExistent')
                     .exists())
        
        self.assertFalse(not_exists)
    
    def test_query_explanation(self):
        """Test query explanation."""
        result = (QueryBuilder(self.index)
                 .where_domain('Science', exact=False)
                 .where_intent('Research', exact=False)
                 .execute())
        
        self.assertIsNotNone(result.query_explanation)
        self.assertIn('domain', result.query_explanation.lower())
        self.assertIn('intent', result.query_explanation.lower())
    
    def test_clone_query(self):
        """Test query cloning."""
        base = (QueryBuilder(self.index)
               .where_domain('Science', exact=False))
        
        bio_query = base.clone().where_intent('Research → Conceptual')
        physics_query = base.clone().where_intent('Research → Applied')
        
        bio_result = bio_query.execute()
        physics_result = physics_query.execute()
        
        self.assertEqual(len(bio_result.items), 1)
        self.assertEqual(len(physics_result.items), 1)
    
    def test_reset_query(self):
        """Test query reset."""
        query = (QueryBuilder(self.index)
                .where_domain('Science', exact=False)
                .where_intent('Research', exact=False))
        
        result_before = query.execute()
        self.assertGreater(len(result_before.items), 0)
        
        query.reset()
        result_after = query.execute()
        
        # After reset, should get all items
        self.assertEqual(len(result_after.items), self.index.count())


class TestFilter(unittest.TestCase):
    """Test Filter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.index = TextIndex()
        
        self.index.add(
            'Research text',
            SemanticDescriptor(
                domain='Science → Biology',
                intent='Research'
            )
        )
        
        self.index.add(
            'Tutorial text',
            SemanticDescriptor(
                domain='Engineering',
                intent='Documentation → Tutorial'
            )
        )
    
    def test_filter_basic(self):
        """Test basic filtering."""
        result = (Filter()
                 .from_index(self.index)
                 .where_domain('Science', exact=False)
                 .execute())
        
        self.assertEqual(len(result), 1)
    
    def test_filter_count(self):
        """Test filter count."""
        count = (Filter()
                .from_index(self.index)
                .where_domain('Science', exact=False)
                .count())
        
        self.assertEqual(count, 1)
    
    def test_filter_first(self):
        """Test filter first."""
        item = (Filter()
               .from_index(self.index)
               .where_domain('Science', exact=False)
               .first())
        
        self.assertIsNotNone(item)
    
    def test_filter_exists(self):
        """Test filter exists."""
        exists = (Filter()
                 .from_index(self.index)
                 .where_domain('Science', exact=False)
                 .exists())
        
        self.assertTrue(exists)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience filter functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.index = TextIndex()
        
        # Research posts
        self.index.add(
            'Biology research',
            SemanticDescriptor(
                domain='Science → Biology',
                intent='Research → Conceptual'
            )
        )
        
        # Tutorial
        self.index.add(
            'Python tutorial',
            SemanticDescriptor(
                domain='Engineering → Software Engineering',
                intent='Documentation → Tutorial',
                audience='Beginners'
            )
        )
        
        self.items = self.index.get_all()
    
    def test_find_research_posts(self):
        """Test find_research_posts function."""
        research = find_research_posts(self.items)
        self.assertEqual(len(research), 1)
    
    def test_find_research_posts_with_domain(self):
        """Test find_research_posts with domain filter."""
        bio_research = find_research_posts(
            self.items,
            domain='Science → Biology'
        )
        self.assertEqual(len(bio_research), 1)
    
    def test_find_tutorials(self):
        """Test find_tutorials function."""
        tutorials = find_tutorials(self.items)
        self.assertEqual(len(tutorials), 1)
    
    def test_find_tutorials_with_domain(self):
        """Test find_tutorials with domain filter."""
        eng_tutorials = find_tutorials(
            self.items,
            domain='Engineering'
        )
        self.assertEqual(len(eng_tutorials), 1)


class TestQueryWithMetadata(unittest.TestCase):
    """Test queries with metadata filters."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.index = TextIndex()
        
        self.index.add(
            'Smith research',
            SemanticDescriptor(domain='Science', intent='Research'),
            metadata={'author': 'Dr. Smith'}
        )
        
        self.index.add(
            'Johnson research',
            SemanticDescriptor(domain='Science', intent='Research'),
            metadata={'author': 'Dr. Johnson'}
        )
    
    def test_metadata_filter(self):
        """Test filtering by metadata."""
        result = (QueryBuilder(self.index)
                 .where_metadata('author', 'Dr. Smith')
                 .execute())
        
        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.items[0].metadata['author'], 'Dr. Smith')
    
    def test_metadata_exists_filter(self):
        """Test filtering by metadata existence."""
        result = (QueryBuilder(self.index)
                 .where_metadata_exists('author')
                 .execute())
        
        self.assertEqual(len(result.items), 2)


class TestQueryWithTimestamps(unittest.TestCase):
    """Test queries with timestamp filters."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.index = TextIndex()
        
        # Add items (they'll have timestamps)
        self.index.add(
            'Old post',
            SemanticDescriptor(domain='Science', intent='Research')
        )
        
        self.index.add(
            'New post',
            SemanticDescriptor(domain='Science', intent='Research')
        )
    
    def test_created_after_filter(self):
        """Test filtering by creation date."""
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        
        result = (QueryBuilder(self.index)
                 .where_created_after(yesterday)
                 .execute())
        
        # Both should be after yesterday
        self.assertEqual(len(result.items), 2)
    
    def test_created_before_filter(self):
        """Test filtering before a date."""
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        
        result = (QueryBuilder(self.index)
                 .where_created_before(tomorrow)
                 .execute())
        
        # Both should be before tomorrow
        self.assertEqual(len(result.items), 2)


class TestQueryExplanation(unittest.TestCase):
    """Test query explanation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.index = TextIndex()
        
        self.index.add(
            'Test',
            SemanticDescriptor(domain='Science', intent='Research')
        )
    
    def test_explain_method(self):
        """Test explain method."""
        query = (QueryBuilder(self.index)
                .where_domain('Science', exact=False)
                .where_intent('Research', exact=False))
        
        explanation = query.explain()
        
        self.assertIn('SELECT', explanation)
        self.assertIn('WHERE', explanation)
    
    def test_build_predicate(self):
        """Test build_predicate method."""
        query = (QueryBuilder(self.index)
                .where_domain('Science', exact=False))
        
        predicate = query.build_predicate()
        self.assertIsNotNone(predicate)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases in querying."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.index = TextIndex()
    
    def test_query_empty_index(self):
        """Test querying empty index."""
        result = (QueryBuilder(self.index)
                 .where_domain('Science', exact=False)
                 .execute())
        
        self.assertEqual(len(result.items), 0)
        self.assertEqual(result.total, 0)
    
    def test_query_no_filters(self):
        """Test query with no filters."""
        self.index.add(
            'Test',
            SemanticDescriptor(domain='Science', intent='Research')
        )
        
        result = QueryBuilder(self.index).execute()
        
        self.assertEqual(len(result.items), 1)
    
    def test_limit_larger_than_results(self):
        """Test limit larger than result count."""
        self.index.add(
            'Test',
            SemanticDescriptor(domain='Science', intent='Research')
        )
        
        result = (QueryBuilder(self.index)
                 .limit(100)
                 .execute())
        
        self.assertEqual(len(result.items), 1)


if __name__ == '__main__':
    unittest.main()
