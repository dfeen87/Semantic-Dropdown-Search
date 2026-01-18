"""
Tests for descriptor validation.
"""

import unittest

from core import (
    SemanticDescriptor,
    SchemaValidator,
    validate,
    normalize_value,
    normalize_descriptor,
)
from core.errors import ValidationError, NormalizationError


class TestDescriptorValidation(unittest.TestCase):
    """Test validation of semantic descriptors."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = SchemaValidator(version="v1")
    
    def test_valid_complete_descriptor(self):
        """Test validation of complete valid descriptor."""
        descriptor = {
            'domain': 'Science → Biology',
            'intent': 'Research → Conceptual',
            'tone': 'Analytical',
            'audience': 'Researchers',
            'stability': 'Hypothesis (Not yet validated)'
        }
        
        result = self.validator.validate_complete_descriptor(descriptor)
        self.assertTrue(result.valid)
        self.assertEqual(len(result.errors), 0)
    
    def test_valid_minimal_descriptor(self):
        """Test validation of minimal descriptor (required fields only)."""
        descriptor = {
            'domain': 'Science',
            'intent': 'Research'
        }
        
        result = self.validator.validate_complete_descriptor(descriptor)
        self.assertTrue(result.valid)
    
    def test_invalid_domain_value(self):
        """Test validation with invalid domain."""
        descriptor = {
            'domain': 'Invalid Domain',
            'intent': 'Research'
        }
        
        result = self.validator.validate_complete_descriptor(descriptor)
        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)
    
    def test_invalid_intent_value(self):
        """Test validation with invalid intent."""
        descriptor = {
            'domain': 'Science',
            'intent': 'Invalid Intent'
        }
        
        result = self.validator.validate_complete_descriptor(descriptor)
        self.assertFalse(result.valid)
    
    def test_missing_required_field_domain(self):
        """Test validation with missing domain."""
        descriptor = {
            'intent': 'Research'
        }
        
        result = self.validator.validate_complete_descriptor(descriptor)
        self.assertFalse(result.valid)
        self.assertTrue(any('domain' in err.lower() for err in result.errors))
    
    def test_missing_required_field_intent(self):
        """Test validation with missing intent."""
        descriptor = {
            'domain': 'Science'
        }
        
        result = self.validator.validate_complete_descriptor(descriptor)
        self.assertFalse(result.valid)
        self.assertTrue(any('intent' in err.lower() for err in result.errors))
    
    def test_partial_validation_allows_missing_required(self):
        """Test that partial validation allows missing required fields."""
        descriptor = {
            'domain': 'Science'
        }
        
        result = self.validator.validate_values(descriptor)
        self.assertTrue(result.valid)
    
    def test_partial_validation_catches_invalid_values(self):
        """Test that partial validation catches invalid values."""
        descriptor = {
            'domain': 'Invalid Domain'
        }
        
        result = self.validator.validate_values(descriptor)
        self.assertFalse(result.valid)
    
    def test_unknown_field_warning(self):
        """Test that unknown fields generate warnings."""
        descriptor = {
            'domain': 'Science',
            'intent': 'Research',
            'unknown_field': 'some value'
        }
        
        result = self.validator.validate_complete_descriptor(descriptor)
        self.assertTrue(result.valid)
        self.assertGreater(len(result.warnings), 0)
    
    def test_hierarchical_domain_validation(self):
        """Test validation of hierarchical domain values."""
        valid_hierarchical = [
            'Science → Biology',
            'Science → Biology → Systems Biology',
            'Engineering → Software Engineering',
        ]
        
        for domain in valid_hierarchical:
            with self.subTest(domain=domain):
                descriptor = {'domain': domain, 'intent': 'Research'}
                result = self.validator.validate_complete_descriptor(descriptor)
                self.assertTrue(result.valid, f"Failed for domain: {domain}")
    
    def test_hierarchical_intent_validation(self):
        """Test validation of hierarchical intent values."""
        valid_hierarchical = [
            'Research',
            'Research → Conceptual',
            'Research → Conceptual → Early-stage',
            'Documentation → Tutorial',
        ]
        
        for intent in valid_hierarchical:
            with self.subTest(intent=intent):
                descriptor = {'domain': 'Science', 'intent': intent}
                result = self.validator.validate_complete_descriptor(descriptor)
                self.assertTrue(result.valid, f"Failed for intent: {intent}")


class TestFieldValidation(unittest.TestCase):
    """Test individual field validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = SchemaValidator(version="v1")
    
    def test_validate_domain_field(self):
        """Test domain field validation."""
        result = self.validator.validate_field('domain', 'Science')
        self.assertTrue(result.valid)
    
    def test_validate_intent_field(self):
        """Test intent field validation."""
        result = self.validator.validate_field('intent', 'Research')
        self.assertTrue(result.valid)
    
    def test_validate_tone_field(self):
        """Test tone field validation."""
        result = self.validator.validate_field('tone', 'Analytical')
        self.assertTrue(result.valid)
    
    def test_validate_audience_field(self):
        """Test audience field validation."""
        result = self.validator.validate_field('audience', 'Researchers')
        self.assertTrue(result.valid)
    
    def test_validate_stability_field(self):
        """Test stability field validation."""
        result = self.validator.validate_field('stability', 'Peer-reviewed')
        self.assertTrue(result.valid)
    
    def test_invalid_field_name(self):
        """Test validation with invalid field name."""
        result = self.validator.validate_field('nonexistent', 'value')
        self.assertFalse(result.valid)


class TestExplainInvalid(unittest.TestCase):
    """Test explain_invalid functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = SchemaValidator(version="v1")
    
    def test_explain_invalid_field(self):
        """Test explanation for invalid field name."""
        explanation = self.validator.explain_invalid('nonexistent', 'value')
        self.assertIn('not recognized', explanation)
        self.assertIn('domain', explanation)  # Should suggest valid fields
    
    def test_explain_invalid_value(self):
        """Test explanation for invalid value."""
        explanation = self.validator.explain_invalid('domain', 'Fake Domain')
        self.assertIn('not allowed', explanation)
        self.assertIn('domain', explanation)
    
    def test_explain_includes_suggestions(self):
        """Test that explanation includes suggestions."""
        explanation = self.validator.explain_invalid('domain', 'Biology')
        # Should suggest related values
        self.assertIn('Science', explanation.lower())


class TestSemanticDescriptorValidation(unittest.TestCase):
    """Test validation through SemanticDescriptor class."""
    
    def test_descriptor_validate_method(self):
        """Test SemanticDescriptor.validate() method."""
        descriptor = SemanticDescriptor(
            domain='Science → Biology',
            intent='Research → Conceptual'
        )
        
        result = descriptor.validate()
        self.assertTrue(result.valid)
    
    def test_descriptor_is_valid_method(self):
        """Test SemanticDescriptor.is_valid() method."""
        descriptor = SemanticDescriptor(
            domain='Science',
            intent='Research'
        )
        
        self.assertTrue(descriptor.is_valid())
    
    def test_descriptor_validate_or_raise_success(self):
        """Test validate_or_raise with valid descriptor."""
        descriptor = SemanticDescriptor(
            domain='Science',
            intent='Research'
        )
        
        # Should not raise
        descriptor.validate_or_raise()
    
    def test_descriptor_validate_or_raise_failure(self):
        """Test validate_or_raise with invalid descriptor."""
        descriptor = SemanticDescriptor(
            domain='Invalid',
            intent='Research'
        )
        
        with self.assertRaises(ValidationError):
            descriptor.validate_or_raise()
    
    def test_descriptor_is_complete(self):
        """Test is_complete method."""
        descriptor = SemanticDescriptor(
            domain='Science',
            intent='Research'
        )
        
        self.assertTrue(descriptor.is_complete())
    
    def test_descriptor_not_complete(self):
        """Test is_complete with partial descriptor."""
        descriptor = SemanticDescriptor(domain='Science')
        
        self.assertFalse(descriptor.is_complete())


class TestNormalization(unittest.TestCase):
    """Test normalization during validation."""
    
    def test_whitespace_normalization(self):
        """Test that whitespace is normalized."""
        descriptor = {
            'domain': '  Science  →  Biology  ',
            'intent': 'Research'
        }
        
        normalized = normalize_descriptor(descriptor)
        self.assertEqual(normalized['domain'], 'Science → Biology')
    
    def test_hierarchy_separator_normalization(self):
        """Test that hierarchy separators are normalized."""
        variations = [
            'Science->Biology',
            'Science -> Biology',
            'Science > Biology',
            'Science→Biology',
        ]
        
        for variation in variations:
            with self.subTest(variation=variation):
                normalized = normalize_value(variation)
                self.assertEqual(normalized, 'Science → Biology')
    
    def test_field_name_normalization(self):
        """Test that field names are normalized."""
        from core.normalize import normalize_field_name
        
        variations = [
            ('Domain', 'domain'),
            ('DOMAIN', 'domain'),
            ('domain-name', 'domain_name'),
        ]
        
        for input_val, expected in variations:
            with self.subTest(input=input_val):
                normalized = normalize_field_name(input_val)
                self.assertEqual(normalized, expected)
    
    def test_normalization_preserves_case(self):
        """Test that normalization preserves value case."""
        value = 'Science → Biology'
        normalized = normalize_value(value)
        self.assertEqual(normalized, value)


class TestConvenienceValidateFunction(unittest.TestCase):
    """Test the convenience validate() function."""
    
    def test_validate_function_complete(self):
        """Test validate() function with complete descriptor."""
        descriptor = {
            'domain': 'Science',
            'intent': 'Research'
        }
        
        result = validate(descriptor)
        self.assertTrue(result.valid)
    
    def test_validate_function_partial(self):
        """Test validate() function with partial flag."""
        descriptor = {
            'domain': 'Science'
        }
        
        result = validate(descriptor, partial=True)
        self.assertTrue(result.valid)
    
    def test_validate_function_invalid(self):
        """Test validate() function with invalid descriptor."""
        descriptor = {
            'domain': 'Invalid',
            'intent': 'Research'
        }
        
        result = validate(descriptor)
        self.assertFalse(result.valid)


class TestValidationResultString(unittest.TestCase):
    """Test ValidationResult string representation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = SchemaValidator(version="v1")
    
    def test_valid_result_string(self):
        """Test string representation of valid result."""
        descriptor = {'domain': 'Science', 'intent': 'Research'}
        result = self.validator.validate_complete_descriptor(descriptor)
        
        result_str = str(result)
        self.assertIn('✓', result_str)
        self.assertIn('passed', result_str.lower())
    
    def test_invalid_result_string(self):
        """Test string representation of invalid result."""
        descriptor = {'domain': 'Invalid', 'intent': 'Research'}
        result = self.validator.validate_complete_descriptor(descriptor)
        
        result_str = str(result)
        self.assertIn('✗', result_str)
        self.assertIn('failed', result_str.lower())
        self.assertGreater(len(result.errors), 0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases in validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = SchemaValidator(version="v1")
    
    def test_empty_descriptor(self):
        """Test validation of empty descriptor."""
        descriptor = {}
        
        result = self.validator.validate_complete_descriptor(descriptor)
        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)
    
    def test_none_values(self):
        """Test handling of None values."""
        descriptor = {
            'domain': 'Science',
            'intent': 'Research',
            'tone': None
        }
        
        # None values should be filtered out by SemanticDescriptor
        desc_obj = SemanticDescriptor.from_dict(descriptor)
        self.assertIsNone(desc_obj.tone)
    
    def test_extra_whitespace_in_values(self):
        """Test handling of extra whitespace."""
        descriptor = {
            'domain': '  Science  ',
            'intent': '  Research  '
        }
        
        normalized = normalize_descriptor(descriptor)
        self.assertEqual(normalized['domain'], 'Science')
        self.assertEqual(normalized['intent'], 'Research')
    
    def test_case_sensitivity(self):
        """Test that validation is case-sensitive."""
        descriptor = {
            'domain': 'science',  # lowercase
            'intent': 'Research'
        }
        
        result = self.validator.validate_complete_descriptor(descriptor)
        # Should fail because 'science' != 'Science'
        self.assertFalse(result.valid)


if __name__ == '__main__':
    unittest.main()
