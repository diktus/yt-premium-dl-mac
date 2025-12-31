import sys
import os
import subprocess
import re
import threading
import customtkinter as ctk
from PIL import Image

def get_resource_path(relative_path):
    """Mendukung py2app (Resource folder di dalam .app bundle)"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    
    # py2app menggunakan environment RESOURCEPATH
    base_path = os.environ.get('RESOURCEPATH', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

class YTProApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.os_platform = sys.platform
        self.internal_bin = get_resource_path("bin")

        # Inisialisasi UI lebih dulu agar fungsi log() bisa bekerja
        self.title("YouTube Premium Pro v1.2.0")
        self.geometry("900x700")
        ctk.set_appearance_mode("dark")
        self.init_ui()

        # Konfigurasi Path khusus macOS (py2app friendly)
        if not self.os_platform.startswith('win'):
            # Kita gunakan folder Application Support agar lebih 'native' dan aman dari sandboxing
            self.bin_dir = os.path.expanduser("~/Library/Application Support/YT_Pro_Bin")
            self.node_path = os.path.join(self.bin_dir, "node")
            self.ytdlp_path = os.path.join(self.bin_dir, "yt-dlp")
            self.setup_mac_binaries()
        else:
            self.bin_dir = self.internal_bin

        # Path Binary Final
        self.node_path = os.path.join(self.bin_dir, "node" + (".exe" if sys.platform == "win32" else ""))
        self.ytdlp_path = os.path.join(self.bin_dir, "yt-dlp" if sys.platform != "win32" else "yt-dlp.exe")

    def setup_mac_binaries(self):
        import shutil
        try:
            os.makedirs(self.bin_dir, exist_ok=True)
            tools = ["node", "yt-dlp", "ffmpeg", "ffprobe"]
            
            for tool in tools:
                src = os.path.join(self.internal_bin, tool)
                dst = os.path.join(self.bin_dir, tool)
                
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    
                    # 1. Hapus atribut karantina (Fix 'App is damaged' atau 'Blocked')
                    subprocess.run(["/usr/bin/xattr", "-cr", dst], stderr=subprocess.DEVNULL)
                    
                    # 2. AD-HOC SIGNING (KUNCI MENGATASI CODE -9)
                    # Ini mendaftarkan binary ke security sistem Mac Anda secara lokal
                    subprocess.run(["/usr/bin/codesign", "--force", "-s", "-", dst], stderr=subprocess.DEVNULL)
                    
                    os.chmod(dst, 0o755) 
            
            self.log("System: Mac Binaries verified & re-signed locally.")
            self.check_binaries()
        except Exception as e:
            self.log(f"Setup Error: {e}")

    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(8, weight=1)

        ctk.CTkLabel(self, text="YOUTUBE DOWNLOADER PRO", font=("Impact", 30)).grid(row=0, column=0, pady=20)
        
        self.txt_urls = ctk.CTkTextbox(self, height=100)
        self.txt_urls.grid(row=1, column=0, padx=20, sticky="ew")
        self.txt_urls.insert("1.0", "Masukkan link video/playlist di sini...")

        # Options
        self.opt_frame = ctk.CTkFrame(self)
        self.opt_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.mode_var = ctk.StringVar(value="video")
        ctk.CTkRadioButton(self.opt_frame, text="Video (1080p+)", variable=self.mode_var, value="video").pack(side="left", padx=10)
        ctk.CTkRadioButton(self.opt_frame, text="Audio (MP3)", variable=self.mode_var, value="audio").pack(side="left", padx=10)
        
        self.is_playlist_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self.opt_frame, text="Download Playlist", variable=self.is_playlist_var).pack(side="left", padx=10)

        # Log area
        self.log_area = ctk.CTkTextbox(self, height=200, fg_color="black", text_color="#00FF00")
        self.log_area.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")

        self.btn_download = ctk.CTkButton(self, text="START DOWNLOAD", command=self.start_thread, height=50, fg_color="green")
        self.btn_download.grid(row=4, column=0, padx=20, pady=20, sticky="ew")

    def log(self, message):
        self.log_area.insert("end", message + "\n")
        self.log_area.see("end")

    def start_thread(self):
        urls = self.txt_urls.get("1.0", "end-1c").strip().split("\n")
        urls = [u.strip() for u in urls if u.strip()]
        if urls:
            self.btn_download.configure(state="disabled")
            threading.Thread(target=self.run_download, args=(urls,), daemon=True).start()

    def check_binaries(self):
        self.log("--- Running Binary Health Check ---")
        
        # Pastikan path absolut
        ffmpeg_exe = os.path.join(self.bin_dir, "ffmpeg")
        
        checks = [
            ("Node.js", [self.node_path, "-v"]),
            ("FFmpeg", [ffmpeg_exe, "-version"]),
            ("YT-DLP", [sys.executable, self.ytdlp_path, "--version"])
        ]

        all_pass = True
        for name, cmd in checks:
            try:
                # Siapkan environment bersih untuk pengetesan
                test_env = os.environ.copy()
                test_env.pop("PYTHONHOME", None)
                test_env.pop("PYTHONPATH", None)
                # Bersihkan path library agar tidak bentrok dengan Python sistem
                test_env.pop("DYLD_LIBRARY_PATH", None)

                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=10,
                    env=test_env
                )
                
                if result.returncode == 0:
                    version_info = result.stdout.split('\n')[0].strip()
                    self.log(f"✅ {name}: {version_info[:50]}...")
                else:
                    self.log(f"❌ {name}: FAILED (Exit Code {result.returncode})")
                    # Tampilkan sedikit detail error jika ada
                    if result.stderr:
                        self.log(f"   Note: {result.stderr[:50]}...")
                    all_pass = False
                    
            except Exception as e:
                self.log(f"❌ {name}: ERROR! ({str(e)[:50]})")
                all_pass = False

        if all_pass:
            self.log("✨ All systems GO! Ready to download.")
        else:
            self.log("⚠️ Warning: Some components might not work correctly.")
            
    def run_download(self, urls):
        dest = os.path.expanduser("~/Downloads")
        abs_bin_path = os.path.realpath(self.bin_dir)
        
        env_vars = os.environ.copy()
        env_vars.pop("PYTHONHOME", None)
        env_vars.pop("PYTHONPATH", None)
        # Penting agar EJS punya tempat menulis cache di Mac
        env_vars["XDG_CACHE_HOME"] = abs_bin_path 
        
        env_vars["PATH"] = f"{abs_bin_path}{os.pathsep}{env_vars.get('PATH', '')}"

        for url in urls:
            try:
                # Perbaikan: --ffmpeg-location harus menunjuk ke FOLDER (abs_bin_path)
                cmd = [
                    sys.executable, "-u", # -u agar log mengalir real-time
                    self.ytdlp_path,
                    "--ffmpeg-location", abs_bin_path, 
                    "--cookies-from-browser", "safari",
                    "--js-runtimes", f"node:{self.node_path}",
                    "--remote-components", "ejs:github",
                    "--no-check-certificate",
                    "--force-ipv4",
                    "-o", os.path.join(dest, "%(title)s.%(ext)s"),
                    "--newline",
                    "--progress"
                ]

                cmd += ["--format-sort", "res,quality,br,size"]
                
                if self.is_playlist_var.get():
                    cmd.append("--yes-playlist")
                else:
                    cmd.append("--no-playlist")

                if self.mode_var.get() == "audio":
                    cmd += ["-f", "bestaudio/best", "--extract-audio", "--audio-format", "mp3", "--audio-quality", "0"]
                else:
                    cmd += ["-f", "bestvideo[height>=1080]+bestaudio/best", "--merge-output-format", "mp4"]

                cmd.append(url.strip())
                
                # Gunakan bufsize=1 agar UI tidak freeze saat baca log
                proc = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT, 
                    text=True, 
                    env=env_vars, 
                    cwd=abs_bin_path,
                    bufsize=1
                )
                
                # Membaca log secara baris demi baris agar tidak stuck
                while True:
                    line = proc.stdout.readline()
                    if not line and proc.poll() is not None:
                        break
                    if line:
                        self.log(line.strip())
                        self.update() # Update UI CustomTkinter
                
                proc.wait()
            except Exception as e:
                self.log(f"Error: {e}")
        
        self.btn_download.configure(state="normal")
        self.log("Selesai!")

if __name__ == "__main__":
    app = YTProApp()
    app.mainloop()