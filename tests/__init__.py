"""
Test suite for Semantic Dropdown Search.

Run all tests:
    python -m unittest discover tests

Run specific test file:
    python -m unittest tests.test_schema
    python -m unittest tests.test_validation
    python -m unittest tests.test_query

Run with coverage:
    coverage run -m unittest discover tests
    coverage report
    coverage html
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))
