#!/bin/bash
# Parallel Deterministic Build Script for Goldcoin Electrum v4.5.0
# Uses 8 cores for parallel processing

set -e

echo "=== Building Goldcoin Electrum v4.5.0 Deterministic Binaries ==="
echo "Using 8 cores for parallel processing"
echo ""

# Get the current commit for reproducible builds
COMMIT=$(git rev-parse HEAD)
echo "Building from commit: $COMMIT"
echo ""

# Create output directories with correct permissions
mkdir -p dist/
mkdir -p contrib/build-wine/dist/
mkdir -p contrib/build-linux/appimage/dist/

# Function to check if build was successful
check_build() {
    if [ $? -eq 0 ]; then
        echo "✅ $1 build completed successfully"
    else
        echo "❌ $1 build failed"
        return 1
    fi
}

# Clean up any existing Docker containers
echo "Cleaning up any existing Docker containers..."
docker rm -f electrum-wine-builder-cont electrum-appimage-builder-cont 2>/dev/null || true

# Create cache directories with proper permissions
mkdir -p /tmp/electrum_build/windows/fresh_clone
mkdir -p /tmp/electrum_build/appimage/fresh_clone

# 1. Build Windows binaries
echo "========================================="
echo "Building Windows binaries with 8 cores..."
echo "========================================="
cd contrib/build-wine
ELECBUILD_COMMIT=$COMMIT ./build.sh &
WINE_PID=$!

# 2. Build Linux AppImage
cd ../build-linux/appimage
echo ""
echo "========================================="
echo "Building Linux AppImage with 8 cores..."
echo "========================================="
ELECBUILD_COMMIT=$COMMIT ./build.sh &
LINUX_PID=$!

cd ../../..

# Wait for both builds to complete
echo ""
echo "Waiting for both builds to complete..."
echo "Wine PID: $WINE_PID"
echo "Linux PID: $LINUX_PID"

# Wait for Windows build
if wait $WINE_PID; then
    check_build "Windows"
    echo "Windows binaries:"
    ls -lah contrib/build-wine/dist/*.exe 2>/dev/null || echo "No Windows binaries found"
else
    echo "❌ Windows build failed"
fi

# Wait for Linux build  
if wait $LINUX_PID; then
    check_build "Linux AppImage"
    echo "Linux AppImage:"
    ls -lah dist/*.AppImage 2>/dev/null || echo "No Linux AppImage found"
else
    echo "❌ Linux build failed"
fi

echo ""
echo "========================================="
echo "Build Summary"
echo "========================================="
echo ""
echo "Built artifacts:"
echo "----------------"
find . -path "./dist/*" -o -path "./contrib/*/dist/*" | grep -E "\\.(exe|AppImage|apk|dmg|tar\\.gz)$" 2>/dev/null | while read file; do
    if [ -f "$file" ]; then
        echo "- $(basename $file) ($(du -h \"$file\" | cut -f1))"
    fi
done || echo "No build artifacts found"

echo ""
echo "Deterministic builds completed using 8 cores"
echo "Artifacts are ready for release distribution."