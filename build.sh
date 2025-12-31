#!/bin/bash

# --- CONFIGURATION ---
VERSION="1.3.0"
RAW_APP_NAME="YT Download.app"
ZIP_NAME="YT-Download-v${VERSION}.zip"

echo "🧹 Cleaning old builds..."
rm -rf build dist

echo "🛠 Building Mac App with py2app..."
python setup.py py2app

# Cek apakah build berhasil
if [ -d "dist/$RAW_APP_NAME" ]; then
    echo "📦 Packaging into ZIP: $ZIP_NAME..."
    cd dist
    # Kompres folder .app menjadi file zip dengan nama versi
    zip -r "$ZIP_NAME" "$RAW_APP_NAME"
    
    echo "🚀 Uploading to GitHub Release..."
    # Perintah ini akan membuat Release dan upload file zip
    gh release create "v$VERSION" "$ZIP_NAME" --title "Release v$VERSION" --notes "Update build v$VERSION"
    
    echo "✨ Process Complete!"
else
    echo "❌ Build failed. Check the errors above."
    exit 1
fi
