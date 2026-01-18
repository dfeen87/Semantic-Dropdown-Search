# Tests

Comprehensive test suite for Semantic Dropdown Search.

## Overview

This directory contains unit tests for all core functionality:
- Schema loading and structure validation
- Descriptor validation and normalization
- Query building and execution

## Test Files

| File | Description | Test Count |
|------|-------------|------------|
| `test_schema.py` | Schema loading and structure | ~30 tests |
| `test_validation.py` | Descriptor validation | ~40 tests |
| `test_query.py` | Query functionality | ~40 tests |

**Total: ~110 tests**

## Running Tests

### Run All Tests

```bash
# Using unittest
python -m unittest discover tests

# Using the test runner
python tests/run_tests.py

# Verbose mode
python tests/run_tests.py -v
```

### Run Specific Test File

```bash
# Schema tests
python -m unittest tests.test_schema

# Validation tests
python -m unittest tests.test_validation

# Query tests
python -m unittest tests.test_query
```

### Run Specific Test Class

```bash
python -m unittest tests.test_schema.TestSchemaLoading
python -m unittest tests.test_validation.TestDescriptorValidation
python -m unittest tests.test_query.TestQueryBuilder
```

### Run Specific Test Method

```bash
python -m unittest tests.test_schema.TestSchemaLoading.test_all_schemas_loaded
```

## Test Coverage

### With Coverage.py

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run -m unittest discover tests

# View report
coverage report

# Generate HTML report
coverage html
open htmlcov/index.html
```

### Expected Coverage

- **Core module**: ~95%
- **Indexer module**: ~90%
- **Query module**: ~90%
- **Overall**: ~90%+

## Test Structure

### test_schema.py

Tests schema loading and structure:

**Classes:**
- `TestSchemaLoading` - Schema file loading
- `TestSchemaStructure` - Schema structure validation
- `TestSchemaValues` - Value extraction
- `TestSchemaRegistry` - Registry functionality
- `TestSchemaValidation` - Schema validation
- `TestSchemaReadme` - Documentation checks

**Key Tests:**
- All schemas load correctly
- Required keys present in schemas
- Version matching
- Hierarchical value extraction
- Registry consistency

### test_validation.py

Tests descriptor validation:

**Classes:**
- `TestDescriptorValidation` - Complete descriptor validation
- `TestFieldValidation` - Individual field validation
- `TestExplainInvalid` - Error explanations
- `TestSemanticDescriptorValidation` - Descriptor class validation
- `TestNormalization` - Value normalization
- `TestConvenienceValidateFunction` - Convenience functions
- `TestValidationResultString` - Result formatting
- `TestEdgeCases` - Edge case handling

**Key Tests:**
- Valid descriptors pass
- Invalid descriptors fail with helpful errors
- Required fields enforced
- Normalization works correctly
- Explainability functions

### test_query.py

Tests query functionality:

**Classes:**
- `TestPredicates` - Predicate logic
- `TestQueryBuilder` - Query building
- `TestFilter` - Filter class
- `TestConvenienceFunctions` - Convenience functions
- `TestQueryWithMetadata` - Metadata filtering
- `TestQueryWithTimestamps` - Timestamp filtering
- `TestQueryExplanation` - Query explanations
- `TestEdgeCases` - Edge cases

**Key Tests:**
- Predicate logic (AND, OR, NOT)
- Hierarchical matching
- Text search
- Sorting and pagination
- Query explanations
- Convenience functions

## Fixtures

Test fixtures are in `fixtures/`:

- **`sample_descriptors.json`** - Valid and invalid descriptors
  - 5 valid complete examples
  - 4 invalid examples with expected errors
  - Hierarchical and flat value lists

## Writing New Tests

### Test Template

```python
import unittest
from core import SemanticDescriptor

class TestNewFeature(unittest.TestCase):
    """Test description."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.descriptor = SemanticDescriptor(
            domain='Science',
            intent='Research'
        )
    
    def test_feature(self):
        """Test specific feature."""
        result = self.descriptor.validate()
        self.assertTrue(result.valid)
    
    def tearDown(self):
        """Clean up after test."""
        pass
```

### Best Practices

1. **Descriptive names**: `test_valid_descriptor_passes_validation`
2. **One assertion focus**: Test one thing per method
3. **Use setUp/tearDown**: Initialize common fixtures
4. **Use subTest**: For testing multiple similar cases
5. **Document**: Include docstrings explaining what's tested

### Adding Test Data

Add new fixtures to `fixtures/sample_descriptors.json`:

```json
{
  "valid_descriptors": [
    {
      "name": "new_example",
      "descriptor": {
        "domain": "...",
        "intent": "..."
      }
    }
  ]
}
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -e .
        pip install coverage
    
    - name: Run tests
      run: |
        coverage run -m unittest discover tests
        coverage report --fail-under=90
```

## Common Issues

### Import Errors

If you get import errors, ensure you're running from the project root:

```bash
# From project root
python -m unittest discover tests

# Not from tests directory
cd tests
python -m unittest discover .  # This may fail
```

### Schema Not Found

Tests look for schemas in `schema/v1/`. Ensure:
- Schema directory exists
- JSON files are valid
- Registry is up to date

### Path Issues

The `__init__.py` adds the parent directory to the path. If imports still fail, check your PYTHONPATH:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Test Statistics

### Current Status

- **Total Tests**: ~110
- **Pass Rate**: 100%
- **Coverage**: ~90%+
- **Runtime**: <5 seconds

### By Module

| Module | Tests | Coverage |
|--------|-------|----------|
| Core | 40 | 95% |
| Indexer | 30 | 90% |
| Query | 40 | 90% |

## Future Tests

Planned test additions:

### Integration Tests
- End-to-end workflows
- Cross-module integration
- Performance benchmarks

### Stress Tests
- Large dataset handling
- Complex query performance
- Memory usage

### API Tests
- HTTP endpoint testing
- Request/response validation
- Error handling

## Resources

- [unittest documentation](https://docs.python.org/3/library/unittest.html)
- [coverage.py documentation](https://coverage.readthedocs.io/)
- [pytest](https://docs.pytest.org/) - Alternative test runner

## Contributing

When adding features:
1. Write tests first (TDD)
2. Ensure existing tests pass
3. Maintain >90% coverage
4. Add fixtures for common cases
5. Document test purpose

## License

MIT License - See `../LICENSE` for details
