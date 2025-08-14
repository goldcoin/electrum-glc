#!/bin/bash
# Deterministic Build Script for Goldcoin Electrum v4.5.0
# This builds reproducible binaries using Docker

set -e

echo "=== Building Goldcoin Electrum v4.5.0 Deterministic Binaries ==="
COMMIT=$(git rev-parse HEAD)
echo "Building from commit: $COMMIT"
echo ""

# Windows Build
echo "========================================="
echo "1/3: Building Windows binaries..."
echo "========================================="
cd contrib/build-wine
export ELECBUILD_COMMIT=$COMMIT
./build.sh
cd ../..
echo "✅ Windows build complete"
ls -lah contrib/build-wine/dist/*.exe 2>/dev/null || echo "Windows binaries will be in contrib/build-wine/dist/"
echo ""

# Linux AppImage Build  
echo "========================================="
echo "2/3: Building Linux AppImage..."
echo "========================================="
cd contrib/build-linux/appimage
export ELECBUILD_COMMIT=$COMMIT
./build.sh
cd ../../..
echo "✅ Linux AppImage build complete"
ls -lah contrib/build-linux/appimage/dist/*.AppImage 2>/dev/null || echo "AppImage will be in contrib/build-linux/appimage/dist/"
echo ""

# Android APK Build
echo "========================================="
echo "3/3: Building Android APK..."
echo "========================================="
if [ -d "contrib/android" ] && [ -f "contrib/android/make_apk.sh" ]; then
    cd contrib/android
    export ELECBUILD_COMMIT=$COMMIT
    ./make_apk.sh
    cd ../..
    echo "✅ Android APK build complete"
    ls -lah contrib/android/dist/*.apk 2>/dev/null || echo "APK will be in contrib/android/dist/"
else
    echo "⚠️  Android build not available"
fi
echo ""

echo "========================================="
echo "✅ All deterministic builds complete!"
echo "========================================="
echo "Artifacts:"
find . -type f \( -name "*.exe" -o -name "*.AppImage" -o -name "*.apk" -o -name "*.tar.gz" \) -path "*/dist/*" 2>/dev/null | while read f; do
    echo "  - $(basename $f) ($(stat -c%s "$f" | numfmt --to=iec))"
done