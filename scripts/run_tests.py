#!/usr/bin/env python3
"""
Script to run tests.
"""

import subprocess
import sys

if __name__ == "__main__":
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])
    sys.exit(result.returncode)