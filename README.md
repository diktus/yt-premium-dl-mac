# 📺 YouTube Downloader Pro v1.3.0

<p align="left">
  <img src="https://img.shields.io/badge/Platform-macOS-000000?style=for-the-badge&logo=apple&logoColor=white" />
  <img src="https://img.shields.io/badge/Core-yt--dlp-FF0000?style=for-the-badge&logo=youtube&logoColor=white" />
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-blue?style=for-the-badge" />
</p>

**YouTube Downloader Pro** is a high-performance macOS GUI wrapper for **[yt-dlp](https://github.com/yt-dlp/yt-dlp)**. Developed with Python and CustomTkinter, it provides a native desktop experience for the world's most powerful command-line media downloader.

> **Created by: DIKTUS**

---

## 🛠️ Core Engine: yt-dlp
This application serves as a specialized interface for **yt-dlp**. While the core engine handles the complex scraping and downloading, this GUI project manages the "macOS overhead," including:

* **Binary Management**: Internal bundling of compatible `yt-dlp`, `FFmpeg`, and `Node.js`.
* **Security Automation**: Built-in **Ad-hoc Signing** and Gatekeeper bypass to ensure binaries run without macOS security errors.
* **JS Runtime Integration**: Automatic linking to Node.js to solve YouTube's *n-challenge* (throttling) encryption.

---

## ✨ Key Features
- 🚀 **Full yt-dlp Power**: Download resolutions from 1080p, 2K, up to 4K using advanced format sorting.
- 🎵 **Premium Audio**: Extract high-bitrate MP3s directly from YouTube Music.
- 🍪 **Multi-Browser Cookies**: Support for **Safari, Chrome, Firefox, Edge, Brave, Opera, and Vivaldi**.
- 📊 **Enhanced Visuals**: Real-time progress bar and speed indicators.
- 📂 **Custom Destination**: Interactive directory selection for your downloads.
- 🛡️ **Health Check**: Automatically verifies and compares binary versions on startup.

---

## ⚠️ IMPORTANT: macOS Permissions (Action Required)

To allow the app to interact with system browsers and execute bundled binaries, you **MUST** configure these settings:

### 1. Grant Full Disk Access
Required for `yt-dlp` to read your browser cookies for Premium access.
1.  Open **System Settings** > **Privacy & Security** > **Full Disk Access**.
2.  Click the **[+]** icon and add `YT_Pro_Mac.app`.
3.  Toggle the switch to **ON**.

### 2. Bypass Gatekeeper
If you see a "damaged" or "unidentified developer" error, run this command in your Terminal:
```bash
xattr -cr /Applications/YT_Pro_Mac.app
```
### 3. Keychain Access
When the app first reads browser cookies, macOS will ask for Keychain permission. Click **"Always Allow"** to enable seamless future downloads.

---

## 🏗️ Development & Build

<details>
<summary><b>View Project Structure</b></summary>

```text
.
├── app_gui.py       # Main GUI Logic & subprocess management
├── bin/             # Required Binaries (yt-dlp, ffmpeg, ffprobe, node)
├── setup.py         # py2app configuration
└── README.md        # Documentation
```
</details>

### Building the .app Bundle
To package the script into a standalone macOS application:
```bash
# 1. Clean previous builds
rm -rf build dist

# 2. Build using py2app
python setup.py py2app

# 3. Clear quarantine flags
xattr -cr dist/YT_Pro_Mac.app
```

---

## 🛡️ Binary Health Check & Version Sync
The app includes a diagnostic suite that runs at launch to verify the three pillars of the application:
1.  ✅ **yt-dlp**: The core downloader engine.
2.  ✅ **Node.js**: The JS runtime for speed-throttling challenges.
3.  ✅ **FFmpeg**: The post-processor for high-quality muxing.

---

## 📝 Legal Disclaimer
This project is a GUI wrapper for `yt-dlp`. It is intended for educational purposes and personal use. Users are responsible for complying with the YouTube Terms of Service and local copyright regulations.

---
<p align="center">
  <b>Created by DIKTUS</b><br>
  Powered by <a href="https://github.com/yt-dlp/yt-dlp">yt-dlp</a>
</p>
