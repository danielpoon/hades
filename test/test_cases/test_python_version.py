#!/usr/bin/env python3.12
"""
Test case: Verify Python version is 3.12
"""

import sys
from typing import Tuple


def test_python_version() -> Tuple[bool, str]:
    """Test if Python version is 3.12."""
    major = sys.version_info.major
    minor = sys.version_info.minor
    
    if major == 3 and minor == 12:
        return True, f"Python version is correct: {sys.version.split()[0]}"
    
    return False, f"Python version is {major}.{minor}, expected 3.12"


if __name__ == "__main__":
    success, message = test_python_version()
    print(f"{'PASS' if success else 'FAIL'}: {message}")
    sys.exit(0 if success else 1)

