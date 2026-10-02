#!/bin/bash
set -e

# --- CONFIGURATION ---
VERSION="1.3.1"
RAW_APP_NAME="YT Download.app"
ZIP_NAME="YT-Download-v${VERSION}.zip"

# Use venv python if available
if [ -f ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
else
    PYTHON_BIN="python3"
fi

echo "🧹 Cleaning old builds..."
rm -rf build dist

if [ ! -f "icon.icns" ]; then
    echo "🎨 Generating Icon..."
    $PYTHON_BIN create_icon.py
else
    echo "ℹ️  Using existing icon.icns (Skipping generation)"
fi

# Ensure bin exists
if [ ! -d "bin" ]; then
    echo "⚠️ bin directory not found! Checking ~/Library/Application Support/YT_Pro_Bin..."
    if [ -d "$HOME/Library/Application Support/YT_Pro_Bin" ]; then
        mkdir -p bin
        cp -R "$HOME/Library/Application Support/YT_Pro_Bin/"* bin/ || true
    fi
fi

echo "🛠 Building Mac App with py2app..."
$PYTHON_BIN setup.py py2app

# Cek apakah build berhasil
if [ -d "dist/$RAW_APP_NAME" ]; then
    # Double check bin in app resources
    if [ -d "bin" ]; then
        echo "📋 Ensuring bin in App Resources..."
        rm -rf "dist/$RAW_APP_NAME/Contents/Resources/bin"
        cp -R bin "dist/$RAW_APP_NAME/Contents/Resources/bin"
        chmod +x dist/"$RAW_APP_NAME"/Contents/Resources/bin/*
    fi

    echo "✍️ Codesigning Application Bundle..."
    xattr -cr "dist/$RAW_APP_NAME"
    codesign --force --deep -s - "dist/$RAW_APP_NAME"

    echo "📦 Packaging into ZIP: $ZIP_NAME..."
    cd dist
    zip -r "$ZIP_NAME" "$RAW_APP_NAME"
    cd ..
    
    if [ "$1" == "--release" ]; then
        echo "🚀 Uploading to GitHub Release..."
        gh release create "v$VERSION" "dist/$ZIP_NAME" --title "Release v$VERSION" --notes "Update build v$VERSION" || echo "⚠️ GitHub release upload failed."
    fi
    
    echo "✨ Process Complete! Built at dist/$RAW_APP_NAME"
else
    echo "❌ Build failed. Check the errors above."
    exit 1
fi
