from setuptools import setup

APP = ['app_gui.py']
DATA_FILES = [
    ('bin', ['bin/ffmpeg', 'bin/ffprobe', 'bin/node', 'bin/yt-dlp'])
]
OPTIONS = {
    'argv_emulation': False,
    'packages': ['customtkinter', 'PIL', 'packaging', 'requests'],
    'includes': ['tkinter', 'requests'],
    'excludes': ['PySide6', 'PyQt6', 'PyQt5'],
    'plist': {
        'CFBundleName': "YT Download",
        'CFBundleDisplayName': "YouTube Premium Pro",
        'CFBundleIdentifier': "com.ytpro.downloader",
        'CFBundleVersion': "1.2.0",
        'LSEnvironment': {
            'PYTHONOPTIMIZE': '1',
        },
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)