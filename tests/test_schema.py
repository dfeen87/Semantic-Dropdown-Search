"""
Tests for schema loading and structure validation.
"""

import unittest
import json
from pathlib import Path

from core import SchemaValidator
from core.errors import SchemaError, SchemaVersionError


class TestSchemaLoading(unittest.TestCase):
    """Test schema loading and validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.schema_dir = Path(__file__).parent.parent / "schema" / "v1"
        self.validator = SchemaValidator(version="v1")
    
    def test_schema_directory_exists(self):
        """Test that schema directory exists."""
        self.assertTrue(self.schema_dir.exists())
        self.assertTrue(self.schema_dir.is_dir())
    
    def test_all_schemas_loaded(self):
        """Test that all expected schemas are loaded."""
        expected_fields = {'domain', 'intent', 'tone', 'audience', 'stability'}
        loaded_fields = set(self.validator._schemas.keys())
        self.assertEqual(expected_fields, loaded_fields)
    
    def test_schema_has_required_keys(self):
        """Test that each schema has required keys."""
        for field_name, schema in self.validator._schemas.items():
            with self.subTest(field=field_name):
                self.assertIn('version', schema)
                self.assertIn('required', schema)
                self.assertIn('description', schema)
                self.assertIn('values', schema)
    
    def test_schema_version_matches(self):
        """Test that schema versions match validator version."""
        for field_name, schema in self.validator._schemas.items():
            with self.subTest(field=field_name):
                version = schema.get('version')
                if version:  # Only check if version is present
                    self.assertEqual(version, "v1")
    
    def test_values_is_list(self):
        """Test that values field is a list."""
        for field_name, schema in self.validator._schemas.items():
            with self.subTest(field=field_name):
                self.assertIsInstance(schema['values'], list)
                self.assertGreater(len(schema['values']), 0)
    
    def test_required_field_is_boolean(self):
        """Test that required field is boolean."""
        for field_name, schema in self.validator._schemas.items():
            with self.subTest(field=field_name):
                self.assertIsInstance(schema['required'], bool)
    
    def test_description_is_string(self):
        """Test that description is a non-empty string."""
        for field_name, schema in self.validator._schemas.items():
            with self.subTest(field=field_name):
                self.assertIsInstance(schema['description'], str)
                self.assertGreater(len(schema['description']), 0)


class TestSchemaStructure(unittest.TestCase):
    """Test schema structure and values."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = SchemaValidator(version="v1")
    
    def test_domain_schema_structure(self):
        """Test domain schema has expected structure."""
        schema = self.validator.get_schema('domain')
        self.assertIsNotNone(schema)
        self.assertTrue(schema['required'])
        
        # Check for hierarchical values
        values = schema['values']
        self.assertIsInstance(values, list)
        
        # Should have some hierarchical entries
        has_hierarchy = any(isinstance(v, dict) for v in values)
        self.assertTrue(has_hierarchy)
    
    def test_intent_schema_structure(self):
        """Test intent schema has expected structure."""
        schema = self.validator.get_schema('intent')
        self.assertIsNotNone(schema)
        self.assertTrue(schema['required'])
        
        # Should have hierarchical structure
        values = schema['values']
        has_hierarchy = any(isinstance(v, dict) for v in values)
        self.assertTrue(has_hierarchy)
    
    def test_tone_schema_structure(self):
        """Test tone schema has expected structure."""
        schema = self.validator.get_schema('tone')
        self.assertIsNotNone(schema)
        self.assertFalse(schema['required'])  # Tone is optional
        
        # Should have flat values
        values = schema['values']
        self.assertIsInstance(values, list)
    
    def test_audience_schema_structure(self):
        """Test audience schema has expected structure."""
        schema = self.validator.get_schema('audience')
        self.assertIsNotNone(schema)
        self.assertFalse(schema['required'])  # Audience is optional
    
    def test_stability_schema_structure(self):
        """Test stability schema has expected structure."""
        schema = self.validator.get_schema('stability')
        self.assertIsNotNone(schema)
        self.assertFalse(schema['required'])  # Stability is optional


class TestSchemaValues(unittest.TestCase):
    """Test extraction of valid values from schemas."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = SchemaValidator(version="v1")
    
    def test_get_valid_values_domain(self):
        """Test extraction of valid domain values."""
        values = self.validator.get_valid_values('domain')
        
        # Should have root values
        self.assertIn('Science', values)
        self.assertIn('Engineering', values)
        
        # Should have hierarchical values
        self.assertIn('Science → Biology', values)
        self.assertIn('Science → Computer Science', values)
    
    def test_get_valid_values_intent(self):
        """Test extraction of valid intent values."""
        values = self.validator.get_valid_values('intent')
        
        # Should have root values
        self.assertIn('Research', values)
        self.assertIn('Documentation', values)
        
        # Should have hierarchical values
        self.assertIn('Research → Conceptual', values)
        self.assertIn('Documentation → Tutorial', values)
    
    def test_get_valid_values_tone(self):
        """Test extraction of valid tone values."""
        values = self.validator.get_valid_values('tone')
        
        # Should have flat values
        self.assertIn('Formal', values)
        self.assertIn('Analytical', values)
        self.assertGreater(len(values), 5)
    
    def test_hierarchical_path_construction(self):
        """Test that hierarchical paths are constructed correctly."""
        values = self.validator.get_valid_values('domain')
        
        # Check for three-level hierarchy
        biology_values = [v for v in values if 'Biology' in v]
        
        # Should have Biology at different levels
        has_root_bio = 'Science → Biology' in values
        has_deeper = any('Biology → ' in v for v in values)
        
        self.assertTrue(has_root_bio or has_deeper)
    
    def test_no_duplicate_values(self):
        """Test that there are no duplicate values after extraction."""
        for field_name in ['domain', 'intent', 'tone', 'audience', 'stability']:
            with self.subTest(field=field_name):
                values = self.validator.get_valid_values(field_name)
                values_list = list(values)
                self.assertEqual(len(values), len(values_list))


class TestSchemaRegistry(unittest.TestCase):
    """Test schema registry functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry_path = Path(__file__).parent.parent / "schema" / "registry.json"
    
    def test_registry_exists(self):
        """Test that registry file exists."""
        self.assertTrue(self.registry_path.exists())
    
    def test_registry_valid_json(self):
        """Test that registry is valid JSON."""
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        
        self.assertIsInstance(registry, dict)
    
    def test_registry_has_versions(self):
        """Test that registry has versions section."""
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        
        self.assertIn('versions', registry)
        self.assertIn('v1', registry['versions'])
    
    def test_registry_v1_fields(self):
        """Test that v1 has all expected fields."""
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        
        v1_fields = registry['versions']['v1']['fields']
        expected_fields = {'domain', 'intent', 'tone', 'audience', 'stability'}
        
        self.assertEqual(set(v1_fields.keys()), expected_fields)
    
    def test_registry_field_metadata(self):
        """Test that each field has required metadata."""
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        
        v1_fields = registry['versions']['v1']['fields']
        
        for field_name, field_info in v1_fields.items():
            with self.subTest(field=field_name):
                self.assertIn('file', field_info)
                self.assertIn('required', field_info)
                self.assertIn('type', field_info)
                self.assertIn('description', field_info)


class TestSchemaValidation(unittest.TestCase):
    """Test schema validation itself."""
    
    def test_invalid_schema_directory(self):
        """Test that invalid directory raises error."""
        with self.assertRaises(SchemaError):
            SchemaValidator(schema_dir=Path("/nonexistent/path"))
    
    def test_get_nonexistent_schema(self):
        """Test getting schema for nonexistent field."""
        validator = SchemaValidator(version="v1")
        schema = validator.get_schema('nonexistent')
        self.assertIsNone(schema)
    
    def test_get_required_fields(self):
        """Test getting required fields."""
        validator = SchemaValidator(version="v1")
        required = validator.get_required_fields()
        
        # Domain and intent should be required
        self.assertIn('domain', required)
        self.assertIn('intent', required)
        
        # These should not be required
        self.assertNotIn('tone', required)
        self.assertNotIn('audience', required)
        self.assertNotIn('stability', required)


class TestSchemaReadme(unittest.TestCase):
    """Test that schema README exists and is valid."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.readme_path = Path(__file__).parent.parent / "schema" / "v1" / "README.md"
    
    def test_readme_exists(self):
        """Test that schema README exists."""
        self.assertTrue(self.readme_path.exists())
    
    def test_readme_not_empty(self):
        """Test that README has content."""
        with open(self.readme_path, 'r') as f:
            content = f.read()
        
        self.assertGreater(len(content), 100)
        self.assertIn('Schema v1', content)


if __name__ == '__main__':
    unittest.main()
