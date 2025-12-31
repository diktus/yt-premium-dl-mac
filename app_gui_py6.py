import sys
import os
import re
import subprocess
import threading
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QTextEdit, QComboBox, 
                             QCheckBox, QLineEdit, QPushButton, QProgressBar, 
                             QFileDialog, QMessageBox, QFrame)
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QFont, QPalette, QColor

# ==========================================
# KONFIGURASI APLIKASI
# ==========================================
APP_VERSION = "1.0.12"

class LoggerSignal(QObject):
    """Helper untuk update UI dari thread berbeda secara aman"""
    log_msg = Signal(str)
    progress_val = Signal(float)
    status_msg = Signal(str, str) # text, color

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class YTDownloaderPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.os_platform = sys.platform
        self.bin_dir = get_resource_path("bin")
        self.signals = LoggerSignal()
        
        # Setup Path Binary
        if self.os_platform.startswith('win'):
            self.node_path = os.path.join(self.bin_dir, "node.exe")
            self.ytdlp_path = os.path.join(self.bin_dir, "yt-dlp.exe")
            self.default_browser = "edge"
        else:
            self.node_path = os.path.join(self.bin_dir, "node")
            self.ytdlp_path = os.path.join(self.bin_dir, "yt-dlp_macos")
            self.default_browser = "safari"

        self.init_macos_security()
        self.init_ui()
        self.setup_connections()
        
        self.log(f"--- SYSTEM INFO ---\nOS: {self.os_platform}\nApp Version: {APP_VERSION}\n-------------------")

    def init_macos_security(self):
        """Bypass Gatekeeper macOS untuk binary di dalam folder bin"""
        if not self.os_platform.startswith('win'):
            try:
                abs_bin = os.path.abspath(self.bin_dir)
                if os.path.exists(abs_bin):
                    subprocess.run(["xattr", "-cr", abs_bin], stderr=subprocess.DEVNULL)
                    for root, dirs, files in os.walk(abs_bin):
                        for f in files:
                            os.chmod(os.path.join(root, f), 0o755)
            except Exception as e:
                print(f"⚠️ Gagal set permission Mac: {e}")

    def init_ui(self):
        self.setWindowTitle(f"YT Premium Pro v{APP_VERSION}")
        self.setMinimumSize(850, 850)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # Header
        header = QLabel("🎬 YT Premium Pro Downloader")
        header.setFont(QFont("Helvetica", 24, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        # URL Input
        self.url_textbox = QTextEdit()
        self.url_textbox.setPlaceholderText("# Masukkan link YouTube di sini (satu link per baris)")
        self.url_textbox.setFixedHeight(140)
        self.url_textbox.setFont(QFont("Courier", 13))
        main_layout.addWidget(self.url_textbox)

        # Settings Group
        settings_frame = QFrame()
        settings_frame.setFrameShape(QFrame.StyledPanel)
        settings_layout = QHBoxLayout(settings_frame)
        
        settings_layout.addWidget(QLabel("Browser Cookies:"))
        self.browser_menu = QComboBox()
        self.browser_menu.addItems(["safari", "chrome", "edge", "firefox", "brave"])
        self.browser_menu.setCurrentText(self.default_browser)
        settings_layout.addWidget(self.browser_menu)

        self.cb_ssl = QCheckBox("Fix SSL")
        self.cb_ssl.setChecked(True)
        settings_layout.addWidget(self.cb_ssl)

        self.cb_ejs = QCheckBox("Use EJS")
        self.cb_ejs.setChecked(True)
        settings_layout.addWidget(self.cb_ejs)

        # FITUR BARU: Checkbox Playlist
        self.cb_playlist = QCheckBox("Download Playlist")
        self.cb_playlist.setChecked(False)
        settings_layout.addWidget(self.cb_playlist)
        
        main_layout.addWidget(settings_frame)

        # Path Selection
        path_frame = QHBoxLayout()
        self.path_entry = QLineEdit(os.path.expanduser("~/Downloads"))
        self.btn_browse = QPushButton("Pilih Folder")
        path_frame.addWidget(self.path_entry)
        path_frame.addWidget(self.btn_browse)
        main_layout.addLayout(path_frame)

        # Mode Selector (Audio vs Video)
        mode_frame = QHBoxLayout()
        self.btn_audio = QPushButton("🔊 AUDIO (MP3)")
        self.btn_audio.setCheckable(True)
        self.btn_audio.setChecked(True)
        self.btn_video = QPushButton("🎥 VIDEO (MP4)")
        self.btn_video.setCheckable(True)
        
        mode_frame.addWidget(self.btn_audio)
        mode_frame.addWidget(self.btn_video)
        main_layout.addLayout(mode_frame)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(15)
        main_layout.addWidget(self.progress_bar)

        # Download Button
        self.btn_download = QPushButton("GAS DOWNLOAD SEKARANG!")
        self.btn_download.setFixedHeight(55)
        self.btn_download.setFont(QFont("Helvetica", 16, QFont.Bold))
        self.btn_download.setStyleSheet("""
            QPushButton { background-color: #1f6aa5; color: white; border-radius: 8px; }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:disabled { background-color: #555555; }
        """)
        main_layout.addWidget(self.btn_download)

        # Logs
        self.log_textbox = QTextEdit()
        self.log_textbox.setReadOnly(True)
        self.log_textbox.setFixedHeight(140)
        self.log_textbox.setFont(QFont("Courier New", 11))
        self.log_textbox.setStyleSheet("background-color: #121212; color: #00FF00; border: 1px solid #333;")
        main_layout.addWidget(self.log_textbox)

        # Status Label
        self.status_label = QLabel("Status: Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Helvetica", 11))
        main_layout.addWidget(self.status_label)

    def setup_connections(self):
        self.btn_browse.clicked.connect(self.browse_folder)
        self.btn_download.clicked.connect(self.start_download_thread)
        self.btn_audio.clicked.connect(lambda: self.toggle_mode("audio"))
        self.btn_video.clicked.connect(lambda: self.toggle_mode("video"))
        
        # Koneksi Signal untuk Update UI dari Thread
        self.signals.log_msg.connect(self.log)
        self.signals.progress_val.connect(self.progress_bar.setValue)
        self.signals.status_msg.connect(self.update_status)

    def toggle_mode(self, mode):
        self.btn_audio.setChecked(mode == "audio")
        self.btn_video.setChecked(mode == "video")

    def update_status(self, text, color):
        self.status_label.setText(f"Status: {text}")
        self.status_label.setStyleSheet(f"color: {color};")

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Pilih Folder Download")
        if folder:
            self.path_entry.setText(folder)

    def log(self, message):
        self.log_textbox.append(message)
        self.log_textbox.ensureCursorVisible()

    def start_download_thread(self):
        urls = [u.strip() for u in self.url_textbox.toPlainText().split("\n") 
                if u.strip() and not u.startswith("#")]
        if not urls:
            QMessageBox.warning(self, "Input Kosong", "Silakan masukkan setidaknya satu link YouTube.")
            return
        
        self.btn_download.setEnabled(False)
        threading.Thread(target=self.run_download, args=(urls,), daemon=True).start()

    def run_download(self, urls):
        mode = "audio" if self.btn_audio.isChecked() else "video"
        dest = self.path_entry.text()
        browser = self.browser_menu.currentText()
        abs_bin_path = os.path.abspath(self.bin_dir)

        env_vars = os.environ.copy()
        env_vars["PATH"] = f"{abs_bin_path}{os.pathsep}{env_vars.get('PATH', '')}"

        for i, url in enumerate(urls):
            self.signals.status_msg.emit(f"Memproses {i+1}/{len(urls)}...", "orange")
            
            cmd = [
                self.ytdlp_path,
                "--ffmpeg-location", abs_bin_path,
                "--cookies-from-browser", browser,
                "--js-runtimes", f"node:{self.node_path}",
                "-o", os.path.join(dest, "%(title)s.%(ext)s"),
                "--newline", "--add-metadata"
            ]

            # Logic Playlist
            if self.cb_playlist.isChecked():
                cmd += ["--yes-playlist"]
            else:
                cmd += ["--no-playlist"]

            if self.cb_ejs.isChecked(): cmd += ["--remote-components", "ejs:github"]
            if self.cb_ssl.isChecked(): cmd += ["--no-check-certificate", "--prefer-insecure"]

            if mode == "audio":
                cmd += ["-f", "bestaudio/best", "--extract-audio", "--audio-format", "mp3", "--audio-quality", "0"]
            else:
                cmd += ["-f", "bestvideo[height>=1080]+bestaudio/best", "--merge-output-format", "mp4"]

            cmd.append(url)

            try:
                si = None
                if self.os_platform.startswith('win'):
                    si = subprocess.STARTUPINFO()
                    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                      text=True, startupinfo=si, env=env_vars)
                
                for line in proc.stdout:
                    clean_line = line.strip()
                    if clean_line:
                        self.signals.log_msg.emit(clean_line)
                        # Regex untuk menangkap progress %
                        match = re.search(r"(\d+\.\d+)%", clean_line)
                        if match:
                            self.signals.progress_val.emit(float(match.group(1)))
                proc.wait()
            except Exception as e:
                self.signals.log_msg.emit(f"❌ Error: {e}")

        self.signals.status_msg.emit("Selesai!", "green")
        self.signals.progress_val.emit(100)
        self.btn_download.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Dark Theme Palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(45, 45, 45))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    window = YTDownloaderPro()
    window.show()
    sys.exit(app.exec())