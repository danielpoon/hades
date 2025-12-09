#!/usr/bin/env python3.12
"""
Test execution script - runs all test cases in test_cases directory
"""

import importlib.util
import sys
from pathlib import Path
from typing import List, Tuple


def run_test_case(test_file: Path) -> Tuple[str, bool, str]:
    """Run a single test case file and return the result."""
    test_name = test_file.stem
    
    try:
        # Load the test module
        spec = importlib.util.spec_from_file_location(test_name, test_file)
        if spec is None or spec.loader is None:
            return test_name, False, f"Failed to load test module: {test_file}"
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[test_name] = module
        spec.loader.exec_module(module)
        
        # Check if test function exists
        if not hasattr(module, f"test_{test_name.replace('test_', '')}"):
            # Try to find any test function
            test_func = None
            for attr_name in dir(module):
                if attr_name.startswith("test_") and callable(getattr(module, attr_name)):
                    test_func = getattr(module, attr_name)
                    break
            
            if test_func is None:
                return test_name, False, "No test function found in module"
        else:
            func_name = f"test_{test_name.replace('test_', '')}"
            test_func = getattr(module, func_name)
        
        # Run the test
        success, message = test_func()
        return test_name, success, message
        
    except Exception as e:
        return test_name, False, f"Test execution error: {e}"


def discover_test_cases(test_dir: Path) -> List[Path]:
    """Discover all test case files in the test_cases directory."""
    if not test_dir.exists():
        return []
    
    test_files = []
    for file in test_dir.iterdir():
        if file.is_file() and file.suffix == ".py" and file.name.startswith("test_"):
            test_files.append(file)
    
    return sorted(test_files)


def main() -> int:
    """Main test execution function."""
    script_dir = Path(__file__).parent
    test_cases_dir = script_dir / "test_cases"
    
    print("=" * 70)
    print("Running Test Suite")
    print("=" * 70)
    print()
    
    # Discover test cases
    test_files = discover_test_cases(test_cases_dir)
    
    if not test_files:
        print("ERROR: No test cases found in test_cases directory")
        return 1
    
    print(f"Found {len(test_files)} test case(s):")
    for test_file in test_files:
        print(f"  - {test_file.name}")
    print()
    
    # Run each test
    results = []
    for test_file in test_files:
        print(f"Running: {test_file.name}...")
        test_name, success, message = run_test_case(test_file)
        status = "PASS" if success else "FAIL"
        print(f"  [{status}] {message}")
        results.append((test_name, success, message))
        print()
    
    # Print summary
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, success, _ in results if success)
    failed = len(results) - passed
    
    for test_name, success, message in results:
        status = "✓" if success else "✗"
        print(f"  {status} {test_name}: {message}")
    
    print()
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    print("=" * 70)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

