#!/bin/bash
# Goldcoin Electrum v4.5.0 Release Build Script
# Run with: sudo ./BUILD_RELEASE.sh

set -e

echo "=== Building Goldcoin Electrum v4.5.0 Release Binaries ==="
echo "This script will build all platform binaries using Docker"
echo ""

# Get the current commit for reproducible builds
COMMIT=$(git rev-parse HEAD)
echo "Building from commit: $COMMIT"
echo ""

# Function to check if build was successful
check_build() {
    if [ $? -eq 0 ]; then
        echo "✅ $1 build completed successfully"
    else
        echo "❌ $1 build failed"
        exit 1
    fi
}

# 1. Build Windows binaries
echo "========================================="
echo "Building Windows binaries..."
echo "========================================="
cd contrib/build-wine
ELECBUILD_COMMIT=$COMMIT ./build.sh
check_build "Windows"
echo "Windows binaries created:"
ls -lah dist/*.exe
cd ../..

# 2. Build Linux AppImage
echo ""
echo "========================================="
echo "Building Linux AppImage..."
echo "========================================="
cd contrib/build-linux/appimage
ELECBUILD_COMMIT=$COMMIT ./build.sh
check_build "Linux AppImage"
echo "Linux AppImage created:"
ls -lah dist/*.AppImage
cd ../../..

# 3. Build Android APK (if directory exists)
if [ -d "contrib/android" ]; then
    echo ""
    echo "========================================="
    echo "Building Android APK..."
    echo "========================================="
    cd contrib/android
    if [ -f "./make_apk.sh" ]; then
        ELECBUILD_COMMIT=$COMMIT ./make_apk.sh
        check_build "Android APK"
        echo "Android APK created:"
        ls -lah dist/*.apk
    else
        echo "⚠️  Android build script not found, skipping..."
    fi
    cd ../..
fi

# 4. Build macOS (only works on macOS hosts)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo ""
    echo "========================================="
    echo "Building macOS DMG..."
    echo "========================================="
    cd contrib/osx
    ./make_osx.sh
    check_build "macOS"
    echo "macOS DMG created:"
    ls -lah dist/*.dmg
    cd ../..
else
    echo ""
    echo "⚠️  Skipping macOS build (requires macOS host)"
fi

echo ""
echo "========================================="
echo "✅ Release Build Complete!"
echo "========================================="
echo ""
echo "Built artifacts:"
echo "----------------"
find . -path "./dist/*" -o -path "./contrib/*/dist/*" | grep -E "\.(exe|AppImage|apk|dmg|tar\.gz)$" | while read file; do
    echo "- $(basename $file) ($(du -h "$file" | cut -f1))"
done

echo ""
echo "All binaries have been built for Goldcoin Electrum v4.5.0"
echo "These files are ready for release distribution."