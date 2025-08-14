#!/bin/bash
# Deterministic requirements installation for Wine build
# This script handles the pip/setuptools wheel hash issue properly

set -e

# First, ensure pip and setuptools are at the correct versions using wheels
# These packages MUST be installed from wheels because their source distributions
# have different hashes than what's in requirements.txt
echo "Installing pip and setuptools from wheels (required for deterministic build)..."
$WINE_PYTHON -m pip install --no-build-isolation --no-dependencies --no-warn-script-location \
    --cache-dir "$WINE_PIP_CACHE_DIR" \
    --only-binary=pip,setuptools \
    pip==24.0 setuptools==69.0.3

# Create a temporary requirements file without pip and setuptools
echo "Preparing requirements without pip and setuptools..."
grep -v "^pip==" "$CONTRIB"/deterministic-build/requirements.txt | \
    grep -v "^setuptools==" > /tmp/requirements-without-pip-setuptools.txt

# Install the rest from source for determinism
echo "Installing remaining requirements from source..."
$WINE_PYTHON -m pip install --no-build-isolation --no-dependencies \
    --no-binary :all: \
    --use-feature=no-binary-enable-wheel-cache \
    --no-warn-script-location \
    --cache-dir "$WINE_PIP_CACHE_DIR" \
    -r /tmp/requirements-without-pip-setuptools.txt

# Clean up
rm -f /tmp/requirements-without-pip-setuptools.txt

echo "Requirements installation complete!"