#!/usr/bin/env python3
"""
Test runner for Semantic Dropdown Search.

Usage:
    python tests/run_tests.py              # Run all tests
    python tests/run_tests.py -v           # Verbose mode
    python tests/run_tests.py schema       # Run only schema tests
    python tests/run_tests.py validation   # Run only validation tests
    python tests/run_tests.py query        # Run only query tests
"""

import sys
import unittest
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))


def run_all_tests(verbosity=2):
    """Run all test suites."""
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_specific_tests(test_name, verbosity=2):
    """Run a specific test module."""
    loader = unittest.TestLoader()
    
    try:
        suite = loader.loadTestsFromName(f'tests.test_{test_name}')
        runner = unittest.TextTestRunner(verbosity=verbosity)
        result = runner.run(suite)
        return result.wasSuccessful()
    except AttributeError:
        print(f"Test module 'test_{test_name}' not found.")
        return False


def print_usage():
    """Print usage information."""
    print(__doc__)


def main():
    """Main test runner."""
    if len(sys.argv) == 1:
        # No arguments, run all tests
        success = run_all_tests()
    elif '-h' in sys.argv or '--help' in sys.argv:
        print_usage()
        return
    elif '-v' in sys.argv:
        # Verbose mode
        success = run_all_tests(verbosity=2)
    else:
        # Run specific test
        test_name = sys.argv[1]
        verbosity = 2 if '-v' in sys.argv else 1
        success = run_specific_tests(test_name, verbosity)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
