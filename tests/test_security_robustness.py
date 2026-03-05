"""
Tests for v1.4.0 security hardening, robustness, and architectural changes.

Covers:
- Path traversal rejection in DirectoryAdapter
- IndexedText.from_dict with missing keys raises IndexingError
- Negative limit/offset raises QueryError
- ID collision detection in TextIndex.add()
- UpdatedBefore predicate
- TextIndex.bulk_load()
- Deserialization bounds checking (max_items)
- SemanticDescriptor.from_json() type validation
- ALTERNATIVE_SEPARATORS no longer includes / or |
- ExplanationString removed (explain_invalid returns plain str)
- STANDARD_FIELDS constant
- Version bump to 1.4.0
"""

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from core import SemanticDescriptor, STANDARD_FIELDS
from core.errors import IndexingError, QueryError, ValidationError
from core.normalize import ALTERNATIVE_SEPARATORS, normalize_value
from indexer import TextIndex, IndexedText
from indexer.adapters import DirectoryAdapter
from indexer.serialize import JSONSerializer, NDJSONSerializer, CSVSerializer
from query import QueryBuilder, UpdatedBefore
from query.predicates import UpdatedBefore as UpdatedBeforePredicate


# -------------------------
# PATH TRAVERSAL
# -------------------------

class TestPathTraversal(unittest.TestCase):
    """Test path traversal rejection in DirectoryAdapter."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.adapter = DirectoryAdapter(Path(self.tmpdir))

    def test_traversal_via_dotdot(self):
        """A path-traversal item_id must raise IndexingError."""
        with self.assertRaises(IndexingError) as ctx:
            self.adapter._item_path("../../etc/passwd")
        self.assertIn("path traversal", str(ctx.exception).lower())

    def test_traversal_via_absolute(self):
        """An absolute-path-like item_id must raise IndexingError."""
        with self.assertRaises(IndexingError):
            # After joining and resolving this would point outside the dir
            self.adapter._item_path("../outside")

    def test_valid_item_id_accepted(self):
        """A simple alphanumeric item_id must not raise."""
        path = self.adapter._item_path("abc-123")
        self.assertTrue(str(path).startswith(self.tmpdir))


# -------------------------
# FROM_DICT MISSING KEYS
# -------------------------

class TestFromDictMissingKeys(unittest.TestCase):
    """Test that IndexedText.from_dict raises IndexingError on missing keys."""

    def _minimal_valid(self):
        return {
            "id": "x",
            "text": "hello",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    def test_valid_dict_succeeds(self):
        d = self._minimal_valid()
        item = IndexedText.from_dict(d)
        self.assertEqual(item.id, "x")

    def test_missing_id_raises(self):
        d = self._minimal_valid()
        del d["id"]
        with self.assertRaises(IndexingError) as ctx:
            IndexedText.from_dict(d)
        self.assertIn("id", str(ctx.exception))

    def test_missing_text_raises(self):
        d = self._minimal_valid()
        del d["text"]
        with self.assertRaises(IndexingError) as ctx:
            IndexedText.from_dict(d)
        self.assertIn("text", str(ctx.exception))

    def test_missing_created_at_raises(self):
        d = self._minimal_valid()
        del d["created_at"]
        with self.assertRaises(IndexingError) as ctx:
            IndexedText.from_dict(d)
        self.assertIn("created_at", str(ctx.exception))

    def test_missing_updated_at_raises(self):
        d = self._minimal_valid()
        del d["updated_at"]
        with self.assertRaises(IndexingError) as ctx:
            IndexedText.from_dict(d)
        self.assertIn("updated_at", str(ctx.exception))

    def test_missing_multiple_keys_raises(self):
        with self.assertRaises(IndexingError):
            IndexedText.from_dict({})


# -------------------------
# NEGATIVE LIMIT / OFFSET
# -------------------------

class TestNegativeLimitOffset(unittest.TestCase):
    """Test that negative limit/offset raise QueryError."""

    def setUp(self):
        self.index = TextIndex()
        self.index.add(
            "test text",
            SemanticDescriptor(domain="Science", intent="Research"),
        )

    def test_negative_limit_raises(self):
        with self.assertRaises(QueryError) as ctx:
            QueryBuilder(self.index).limit(-1)
        self.assertIn("limit", str(ctx.exception).lower())

    def test_negative_offset_raises(self):
        with self.assertRaises(QueryError) as ctx:
            QueryBuilder(self.index).offset(-1)
        self.assertIn("offset", str(ctx.exception).lower())

    def test_zero_limit_allowed(self):
        result = QueryBuilder(self.index).limit(0).execute()
        self.assertEqual(len(result.items), 0)

    def test_zero_offset_allowed(self):
        result = QueryBuilder(self.index).offset(0).execute()
        self.assertEqual(len(result.items), 1)


# -------------------------
# ID COLLISION DETECTION
# -------------------------

class TestIdCollisionDetection(unittest.TestCase):
    """Test that duplicate item IDs are rejected in TextIndex.add()."""

    def setUp(self):
        self.index = TextIndex()

    def test_duplicate_id_raises(self):
        self.index.add(
            "first text",
            SemanticDescriptor(domain="Science", intent="Research"),
            item_id="my-id",
        )
        with self.assertRaises(IndexingError) as ctx:
            self.index.add(
                "different text",
                SemanticDescriptor(domain="Science", intent="Research"),
                item_id="my-id",
            )
        self.assertIn("my-id", str(ctx.exception))
        self.assertIn("already exists", str(ctx.exception))

    def test_auto_generated_id_no_collision(self):
        item1 = self.index.add(
            "text one",
            SemanticDescriptor(domain="Science", intent="Research"),
        )
        item2 = self.index.add(
            "text two",
            SemanticDescriptor(domain="Science", intent="Research"),
        )
        self.assertNotEqual(item1.id, item2.id)


# -------------------------
# UPDATED_BEFORE PREDICATE
# -------------------------

class TestUpdatedBeforePredicate(unittest.TestCase):
    """Test the UpdatedBefore predicate."""

    def setUp(self):
        self.index = TextIndex()
        self.item = self.index.add(
            "test text",
            SemanticDescriptor(domain="Science", intent="Research"),
        )

    def test_updated_before_matches_past_item(self):
        future = datetime.now(timezone.utc) + timedelta(days=1)
        pred = UpdatedBeforePredicate(future)
        self.assertTrue(pred.test(self.item))

    def test_updated_before_rejects_future_cutoff_in_past(self):
        past = datetime.now(timezone.utc) - timedelta(days=1)
        pred = UpdatedBeforePredicate(past)
        self.assertFalse(pred.test(self.item))

    def test_updated_before_explain(self):
        ts = datetime(2025, 1, 1, tzinfo=timezone.utc)
        pred = UpdatedBeforePredicate(ts)
        self.assertIn("updated before", pred.explain())

    def test_query_builder_where_updated_before(self):
        future = datetime.now(timezone.utc) + timedelta(days=1)
        result = QueryBuilder(self.index).where_updated_before(future).execute()
        self.assertEqual(len(result.items), 1)

    def test_query_builder_where_updated_before_filters_correctly(self):
        past = datetime.now(timezone.utc) - timedelta(days=1)
        result = QueryBuilder(self.index).where_updated_before(past).execute()
        self.assertEqual(len(result.items), 0)

    def test_updated_before_exported_from_query(self):
        """UpdatedBefore must be importable from the query package."""
        self.assertIs(UpdatedBefore, UpdatedBeforePredicate)


# -------------------------
# BULK LOAD
# -------------------------

class TestBulkLoad(unittest.TestCase):
    """Test TextIndex.bulk_load()."""

    def _make_item(self, text, item_id=None):
        now = datetime.now(timezone.utc)
        import hashlib
        content_hash = hashlib.sha256(text.encode()).hexdigest()
        return IndexedText(
            id=item_id or text,
            text=text,
            descriptor=SemanticDescriptor(domain="Science", intent="Research"),
            created_at=now,
            updated_at=now,
            content_hash=content_hash,
        )

    def test_bulk_load_populates_index(self):
        items = [self._make_item(f"text {i}", f"id-{i}") for i in range(5)]
        index = TextIndex()
        index.bulk_load(items)
        self.assertEqual(index.count(), 5)

    def test_bulk_load_hash_to_id_populated(self):
        item = self._make_item("hello world", "hw")
        index = TextIndex()
        index.bulk_load([item])
        self.assertEqual(index._hash_to_id[item.content_hash], "hw")

    def test_bulk_load_items_retrievable(self):
        item = self._make_item("some content", "my-item")
        index = TextIndex()
        index.bulk_load([item])
        retrieved = index.get("my-item")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.text, "some content")

    def test_from_list_uses_bulk_load(self):
        """TextIndex.from_list() should produce a correctly populated index."""
        data = [
            {
                "id": "a",
                "text": "alpha",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        ]
        index = TextIndex.from_list(data, validate_on_add=False)
        self.assertEqual(index.count(), 1)
        self.assertIsNotNone(index.get("a"))


# -------------------------
# DESERIALIZATION BOUNDS
# -------------------------

class TestDeserializationBounds(unittest.TestCase):
    """Test max_items parameter on deserializers."""

    def _sample_item_dict(self, text="hello"):
        return {
            "id": text,
            "text": text,
            "descriptor": {},
            "metadata": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "content_hash": "",
        }

    # ---- JSON ----

    def test_json_deserialize_within_limit(self):
        data = json.dumps([self._sample_item_dict(f"item{i}") for i in range(3)])
        items = JSONSerializer.deserialize(data, max_items=5)
        self.assertEqual(len(items), 3)

    def test_json_deserialize_exceeds_limit_raises(self):
        data = json.dumps([self._sample_item_dict(f"item{i}") for i in range(5)])
        with self.assertRaises(IndexingError) as ctx:
            JSONSerializer.deserialize(data, max_items=3)
        self.assertIn("max_items", str(ctx.exception))

    def test_json_deserialize_no_limit(self):
        data = json.dumps([self._sample_item_dict(f"item{i}") for i in range(100)])
        items = JSONSerializer.deserialize(data)
        self.assertEqual(len(items), 100)

    # ---- NDJSON ----

    def test_ndjson_deserialize_within_limit(self):
        lines = "\n".join(
            json.dumps(self._sample_item_dict(f"item{i}")) for i in range(3)
        )
        items = NDJSONSerializer.deserialize(lines, max_items=5)
        self.assertEqual(len(items), 3)

    def test_ndjson_deserialize_exceeds_limit_raises(self):
        lines = "\n".join(
            json.dumps(self._sample_item_dict(f"item{i}")) for i in range(5)
        )
        with self.assertRaises(IndexingError) as ctx:
            NDJSONSerializer.deserialize(lines, max_items=2)
        self.assertIn("max_items", str(ctx.exception))

    # ---- CSV ----

    def test_csv_deserialize_within_limit(self):
        from indexer.serialize import CSVSerializer

        items_obj = []
        for i in range(3):
            d = self._sample_item_dict(f"item{i}")
            items_obj.append(IndexedText.from_dict(d))

        csv_data = CSVSerializer.serialize(items_obj)
        result = CSVSerializer.deserialize(csv_data, max_items=5)
        self.assertEqual(len(result), 3)

    def test_csv_deserialize_exceeds_limit_raises(self):
        from indexer.serialize import CSVSerializer

        items_obj = []
        for i in range(5):
            d = self._sample_item_dict(f"item{i}")
            items_obj.append(IndexedText.from_dict(d))

        csv_data = CSVSerializer.serialize(items_obj)
        with self.assertRaises(IndexingError) as ctx:
            CSVSerializer.deserialize(csv_data, max_items=2)
        self.assertIn("max_items", str(ctx.exception))


# -------------------------
# FROM_JSON TYPE VALIDATION
# -------------------------

class TestFromJsonTypeValidation(unittest.TestCase):
    """Test SemanticDescriptor.from_json() validates JSON type."""

    def test_valid_json_object(self):
        d = SemanticDescriptor.from_json('{"domain": "Science", "intent": "Research"}')
        self.assertEqual(d.domain, "Science")

    def test_json_list_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            SemanticDescriptor.from_json('["Science", "Research"]')

    def test_json_integer_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            SemanticDescriptor.from_json('42')

    def test_json_null_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            SemanticDescriptor.from_json('null')

    def test_json_string_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            SemanticDescriptor.from_json('"just a string"')


# -------------------------
# SEPARATOR NORMALIZATION
# -------------------------

class TestSeparatorNormalization(unittest.TestCase):
    """Test that / and | are no longer treated as hierarchy separators."""

    def test_slash_preserved(self):
        """A lone slash should NOT be normalized to the hierarchy separator."""
        value = "Analytical / Cautious"
        normalized = normalize_value(value)
        self.assertIn("/", normalized)
        self.assertNotIn("→", normalized)

    def test_pipe_preserved(self):
        """A lone pipe should NOT be normalized to the hierarchy separator."""
        value = "Option A | Option B"
        normalized = normalize_value(value)
        self.assertIn("|", normalized)
        self.assertNotIn("→", normalized)

    def test_slash_not_in_alternative_separators(self):
        self.assertNotIn("/", ALTERNATIVE_SEPARATORS)
        self.assertNotIn(" / ", ALTERNATIVE_SEPARATORS)

    def test_pipe_not_in_alternative_separators(self):
        self.assertNotIn("|", ALTERNATIVE_SEPARATORS)
        self.assertNotIn(" | ", ALTERNATIVE_SEPARATORS)

    def test_arrow_still_normalized(self):
        """'->' should still be normalized."""
        normalized = normalize_value("Science->Biology")
        self.assertEqual(normalized, "Science → Biology")

    def test_gt_still_normalized(self):
        """' > ' should still be normalized."""
        normalized = normalize_value("Science > Biology")
        self.assertEqual(normalized, "Science → Biology")


# -------------------------
# STANDARD_FIELDS CONSTANT
# -------------------------

class TestStandardFieldsConstant(unittest.TestCase):
    """Test that STANDARD_FIELDS is exported and correct."""

    def test_standard_fields_is_frozenset(self):
        self.assertIsInstance(STANDARD_FIELDS, frozenset)

    def test_standard_fields_contains_expected(self):
        expected = {'domain', 'intent', 'tone', 'audience', 'stability'}
        self.assertEqual(STANDARD_FIELDS, expected)

    def test_standard_fields_importable_from_core(self):
        from core import STANDARD_FIELDS as SF
        self.assertIsNotNone(SF)


# -------------------------
# COUNT USES TOTAL
# -------------------------

class TestCountUsesPaginatedTotal(unittest.TestCase):
    """Test that QueryBuilder.count() returns total, not post-pagination count."""

    def setUp(self):
        self.index = TextIndex()
        for i in range(5):
            self.index.add(
                f"text {i}",
                SemanticDescriptor(domain="Science", intent="Research"),
            )

    def test_count_without_limit_equals_total(self):
        count = QueryBuilder(self.index).count()
        self.assertEqual(count, 5)

    def test_count_ignores_limit(self):
        """count() should return the total matching items, ignoring limit."""
        count = QueryBuilder(self.index).limit(2).count()
        self.assertEqual(count, 5)

    def test_count_ignores_offset(self):
        """count() should return the total matching items, ignoring offset."""
        count = QueryBuilder(self.index).offset(3).count()
        self.assertEqual(count, 5)


# -------------------------
# VERSION
# -------------------------

class TestVersion(unittest.TestCase):
    """Test that version has been bumped to 1.4.0."""

    def test_core_version(self):
        import core
        self.assertEqual(core.__version__, "1.4.0")

    def test_version_file(self):
        version_file = Path(__file__).parent.parent / "VERSION"
        self.assertEqual(version_file.read_text().strip(), "1.4.0")


# -------------------------
# EXPLANATION STRING REMOVED
# -------------------------

class TestExplanationStringRemoved(unittest.TestCase):
    """Test that ExplanationString is gone and explain_invalid returns plain str."""

    def test_explain_invalid_returns_plain_str(self):
        from core.validate import SchemaValidator
        validator = SchemaValidator(version="v1")
        explanation = validator.explain_invalid("domain", "Fake Domain")
        self.assertIsInstance(explanation, str)
        # Calling lower() should actually lower the string now
        lowered = explanation.lower()
        self.assertEqual(lowered, explanation.lower())
        # Verify no ExplanationString subclass
        self.assertIs(type(explanation), str)

    def test_explanation_string_not_in_validate_module(self):
        import core.validate as cv
        self.assertFalse(hasattr(cv, "ExplanationString"))


if __name__ == "__main__":
    unittest.main()
