📺 YouTube Downloader Pro v1.3.0
YouTube Downloader Pro is a powerful macOS GUI wrapper for yt-dlp. Built with Python (CustomTkinter), it simplifies the process of downloading high-quality content by managing complex backend binaries, macOS security permissions, and encryption challenges automatically.

Created by: DIKTUS

🛠️ Core Engine: yt-dlp
This application uses yt-dlp as its primary engine. While yt-dlp is typically a command-line tool, this project provides a native macOS experience by:

Managing Binaries: Bundling compatible versions of yt-dlp, FFmpeg, and Node.js.

Security Automation: Automatically handling macOS Gatekeeper and code-signing requirements.

Visual Interface: Providing a user-friendly way to use advanced yt-dlp arguments (cookies, format sorting, and EJS solvers).

✨ Key Features
🚀 Full yt-dlp Power: Supports resolutions from 1080p, 2K, up to 4K via yt-dlp's format sorting.

🎵 Audio Extraction: High-bitrate MP3 conversion powered by FFmpeg.

🍪 Premium & Browser Integration: Seamlessly pass cookies from Safari, Chrome, Firefox, Edge, Brave, and more to yt-dlp for Premium/Member-only content.

📦 Zero Dependency for Users: Standalone .app bundle with internal Node.js to solve YouTube's n-challenge encryption.

📊 Visual Feedback: Progress bar and speed indicator parsed directly from yt-dlp output.

🛠️ Diagnostic Check: Built-in health check to ensure yt-dlp and its helper binaries are functional.

⚠️ IMPORTANT: macOS Security Settings (Required)
Because the app interacts with system-level browser data to provide Premium features, you MUST follow these steps:

1. Grant Full Disk Access

Required for yt-dlp to read browser cookies securely.

Go to System Settings > Privacy & Security > Full Disk Access.

Click the [+] icon and add YT_Pro_Mac.app.

Ensure the toggle is switched to ON.

2. Bypass Gatekeeper

If the app shows an "unidentified developer" or "damaged" error, run this in your Terminal:

Bash
xattr -cr /Applications/YT_Pro_Mac.app
3. Keychain Permissions

When yt-dlp first attempts to access browser cookies, macOS will prompt for Keychain access. Click "Always Allow" to prevent being asked every time you download.

🏗️ Build & Development
Project Structure

Plaintext
YT_Pro_Mac/
├── app_gui.py       # Main GUI logic
├── bin/             # Core Binaries (yt-dlp, ffmpeg, ffprobe, node)
├── Resources/       # UI Icons and images
└── setup.py         # py2app configuration
Building the Standalone App

To package the script into a native .app bundle:

Bash
rm -rf build dist
python setup.py py2app
# Code-sign and clear quarantine
xattr -cr dist/YT_Pro_Mac.app
🛡️ Binary Health Check
Upon startup, the GUI verifies the three pillars of the application:

✅ yt-dlp: The core downloader.

✅ Node.js: The JavaScript runtime for solving speed-throttling challenges.

✅ FFmpeg: The post-processor for high-quality muxing.

📝 Disclaimer
This tool is a GUI wrapper for yt-dlp. Users are responsible for complying with YouTube's Terms of Service and local copyright laws.

Created by DIKTUS | Powered by yt-dlp
