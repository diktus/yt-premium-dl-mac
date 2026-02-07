from setuptools import setup

APP = ['app_gui.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'packages': ['customtkinter', 'PIL', 'packaging', 'requests'],
    'includes': ['tkinter'],
    'excludes': ['PySide6', 'PyQt6', 'PyQt5', 'setuptools', 'distutils'],
    'resources': ['bin'],
    'iconfile': 'icon.icns',
    'plist': {
        'CFBundleName': "YT Download",
        'CFBundleDisplayName': "YouTube Premium Pro",
        'CFBundleIdentifier': "com.ytpro.downloader",
        'CFBundleVersion': "1.3.1",
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