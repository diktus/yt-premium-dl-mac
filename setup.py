import os
import shutil
import subprocess
from setuptools import setup

try:
    from py2app.build_app import py2app as _py2app

    class CustomPy2App(_py2app):
        def run(self):
            super().run()
            app_name = self.get_appname()
            res_dir = os.path.join(self.dist_dir, f"{app_name}.app", "Contents", "Resources")
            src_bin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
            if os.path.exists(src_bin):
                dst_bin = os.path.join(res_dir, "bin")
                shutil.rmtree(dst_bin, ignore_errors=True)
                shutil.copytree(src_bin, dst_bin)
                for f in os.listdir(dst_bin):
                    fp = os.path.join(dst_bin, f)
                    if os.path.isfile(fp):
                        os.chmod(fp, 0o755)
                        subprocess.run(["/usr/bin/xattr", "-cr", fp], stderr=subprocess.DEVNULL)
                        subprocess.run(["/usr/bin/codesign", "--force", "-s", "-", fp], stderr=subprocess.DEVNULL)
except ImportError:
    CustomPy2App = None

APP = ['app_gui.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'packages': ['customtkinter', 'PIL', 'packaging', 'requests'],
    'includes': ['tkinter'],
    'excludes': ['PySide6', 'PyQt6', 'PyQt5', 'setuptools', 'distutils'],
    'resources': [],
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

cmdclass = {'py2app': CustomPy2App} if CustomPy2App else {}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    cmdclass=cmdclass,
    setup_requires=['py2app'],
)