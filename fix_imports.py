#!/usr/bin/env python3
"""Fix import sorting using isort configuration from pyproject.toml"""

import subprocess
import sys

# isort is configured in pyproject.toml with:
# profile = "black"
# line_length = 100
# known_first_party = ["electrum"]

print("Running isort to fix import organization...")
result = subprocess.run([
    sys.executable, "-m", "isort",
    "--profile", "black",
    "--line-length", "100",
    "--known-first-party", "electrum",
    "electrum/"
], capture_output=True, text=True)

if result.returncode == 0:
    print("✓ Import organization fixed successfully")
else:
    print(f"Error: {result.stderr}")
    sys.exit(1)