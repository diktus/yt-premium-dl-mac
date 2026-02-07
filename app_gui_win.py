import sys
import os
import subprocess
import re
import threading
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
import requests
import json
import shutil

def get_resource_path(relative_path):
    """Mendukung PyInstaller (Resource folder di dalam .exe bundle)"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    base_path = os.environ.get('RESOURCEPATH', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

class YTProApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.internal_bin = get_resource_path("bin")
        
        # Inisialisasi variabel setting
        self.download_path = ctk.StringVar(value=os.path.expanduser("~/Downloads"))

        # Inisialisasi UI
        self.title("YouTube Premium Pro Downloader v1.3.1 (Windows)")
        self.geometry("900x850")
        ctk.set_appearance_mode("dark")
        self.init_ui()

        # Konfigurasi Path khusus Windows
        # Menggunakan APPDATA agar writeable dan terpisah dari instalasi program
        self.bin_dir = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "YT_Pro_Bin")
        self.node_path = os.path.join(self.bin_dir, "node.exe")
        self.ytdlp_path = os.path.join(self.bin_dir, "yt-dlp.exe")
        
        self.setup_windows_binaries()

    def setup_windows_binaries(self):
        try:
            os.makedirs(self.bin_dir, exist_ok=True)
            # Daftar tools yang dibutuhkan di Windows
            tools = ["node.exe", "yt-dlp.exe", "ffmpeg.exe", "ffprobe.exe"]
            
            for tool in tools:
                src = os.path.join(self.internal_bin, tool)
                dst = os.path.join(self.bin_dir, tool)
                
                # Hanya copy jika file tujuan BELUM ada
                if not os.path.exists(dst):
                    if os.path.exists(src):
                        shutil.copy2(src, dst)
                    else:
                        # Fallback: Coba cari tanpa ekstensi (jika source dari mac) lalu rename
                        src_no_ext = os.path.splitext(src)[0]
                        if os.path.exists(src_no_ext):
                             shutil.copy2(src_no_ext, dst)
                        else:
                             self.log(f"⚠️ Warning: Source binary {tool} not found in {self.internal_bin}")

            self.log("System: Windows Binaries verified.")
            self.check_binaries()
        except Exception as e:
            self.log(f"Setup Error: {e}")

    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="YOUTUBE PREMIUM DOWNLOADER", font=("Impact", 35)).grid(row=0, column=0, pady=(20, 10))
        ctk.CTkLabel(self, text="created by diktus", font=("Arial", 15)).grid(row=1, column=0, pady=(0, 20))
        
        # URL Input
        self.txt_urls = ctk.CTkTextbox(self, height=120)
        self.txt_urls.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.txt_urls.insert("1.0", "Masukkan link video/playlist di sini...")

        # Settings Frame
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.settings_frame.grid_columnconfigure(1, weight=1)

        # Folder Selection
        ctk.CTkLabel(self.settings_frame, text="Download To:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.lbl_path = ctk.CTkEntry(self.settings_frame, textvariable=self.download_path, state="disabled", fg_color="transparent")
        self.lbl_path.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(self.settings_frame, text="Browse", width=80, command=self.browse_folder).grid(row=0, column=2, padx=10, pady=5)

        # Cookie Browser Selection
        ctk.CTkLabel(self.settings_frame, text="Cookies From:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.browser_var = ctk.StringVar(value="chrome")
        self.browser_menu = ctk.CTkOptionMenu(self.settings_frame, values=["chrome", "firefox", "edge", "brave", "opera", "vivaldi"], variable=self.browser_var)
        self.browser_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkButton(self.settings_frame, text="Update Core", width=80, fg_color="#e67e22", hover_color="#d35400", command=self.update_ytdlp).grid(row=1, column=2, padx=10, pady=5)

        # Mode Options
        self.opt_frame = ctk.CTkFrame(self)
        self.opt_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.mode_var = ctk.StringVar(value="video")
        ctk.CTkRadioButton(self.opt_frame, text="Video (1080p+)", variable=self.mode_var, value="video").pack(side="left", padx=20, pady=10)
        ctk.CTkRadioButton(self.opt_frame, text="Audio (best/.m4a)", variable=self.mode_var, value="audio_m4a").pack(side="left", padx=20, pady=10)
        ctk.CTkRadioButton(self.opt_frame, text="Audio (MP3)", variable=self.mode_var, value="audio_mp3").pack(side="left", padx=20, pady=10)
        self.is_playlist_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self.opt_frame, text="Download Playlist", variable=self.is_playlist_var).pack(side="left", padx=20, pady=10)

        # Visual Progress Frame
        self.progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.progress_frame.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, orientation="horizontal")
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=5)
        
        self.lbl_status = ctk.CTkLabel(self.progress_frame, text="Ready", font=("Arial", 12))
        self.lbl_status.pack(side="left")
        self.lbl_speed = ctk.CTkLabel(self.progress_frame, text="0 MB/s", font=("Arial", 12, "bold"), text_color="cyan")
        self.lbl_speed.pack(side="right")

        # Log area
        self.log_area = ctk.CTkTextbox(self, height=200, fg_color="black", text_color="#00FF00", font=("Courier New", 12))
        self.log_area.grid(row=6, column=0, padx=20, pady=10, sticky="nsew")

        self.btn_download = ctk.CTkButton(self, text="START DOWNLOAD", command=self.start_thread, height=60, font=("Arial", 18, "bold"), fg_color="#2ecc71", hover_color="#27ae60")
        self.btn_download.grid(row=7, column=0, padx=20, pady=20, sticky="ew")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_path.set(folder)

    def log(self, message):
        self.log_area.insert("end", message + "\n")
        self.log_area.see("end")

    def get_latest_ytdlp_version(self):
        try:
            response = requests.get("https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest", timeout=5)
            response.raise_for_status()
            return response.json()["tag_name"]
        except (requests.RequestException, KeyError, json.JSONDecodeError) as e:
            self.log(f"Could not fetch latest yt-dlp version: {e}")
            return None

    def check_binaries(self):
        self.log("--- Running Binary Health Check ---")
        ffmpeg_exe = os.path.join(self.bin_dir, "ffmpeg.exe")
        
        # Windows: Run exe directly
        ytdlp_cmd = [self.ytdlp_path, "--version"]
        
        checks = [
            ("Node.js", [self.node_path, "-v"]),
            ("FFmpeg", [ffmpeg_exe, "-version"]),
            ("YT-DLP", ytdlp_cmd)
        ]
        all_pass = True
        
        latest_ytdlp_version = self.get_latest_ytdlp_version()

        for name, cmd in checks:
            try:
                # Windows: Hide console window for checks
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                test_env = os.environ.copy()
                test_env.pop("PYTHONHOME", None)
                test_env.pop("PYTHONPATH", None)
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, env=test_env, startupinfo=startupinfo)
                if result.returncode == 0:
                    version = result.stdout.split('\n')[0].strip()
                    if name == "YT-DLP" and latest_ytdlp_version:
                        if version == latest_ytdlp_version:
                            self.log(f"✅ {name}: {version} (Up to date)")
                        else:
                            self.log(f"⚠️ {name}: {version} (Newer version available: {latest_ytdlp_version})")
                    else:
                        self.log(f"✅ {name}: {version[:50]}...")
                else:
                    raise Exception(result.stderr)
            except Exception as e:
                self.log(f"❌ {name}: ERROR! ({str(e)[:50]})")
                all_pass = False
        if all_pass: self.log("✨ All systems GO!")

    def update_ytdlp(self):
        self.log("--- Updating yt-dlp ---")
        # Windows URL: .exe
        url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
        try:
            self.log("Downloading latest binary...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            temp_path = self.ytdlp_path + ".new"
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            if os.path.exists(self.ytdlp_path):
                os.remove(self.ytdlp_path)
            os.rename(temp_path, self.ytdlp_path)
            
            self.log("✅ yt-dlp updated successfully!")
            self.check_binaries()
        except Exception as e:
            self.log(f"❌ Update failed: {e}")

    def start_thread(self):
        urls = self.txt_urls.get("1.0", "end-1c").strip().split("\n")
        urls = [u.strip() for u in urls if u.strip()]
        if urls:
            self.btn_download.configure(state="disabled", text="DOWNLOADING...")
            threading.Thread(target=self.run_download, args=(urls,), daemon=True).start()

    def update_progress(self, line):
        percent_match = re.search(r'(\d+\.\d+)%', line)
        if percent_match:
            percent = float(percent_match.group(1)) / 100
            self.progress_bar.set(percent)
            self.lbl_status.configure(text=f"Downloading... {percent_match.group(1)}%")
            
        speed_match = re.search(r'at\s+([\d\.]+\w+/s)', line)
        if speed_match:
            self.lbl_speed.configure(text=speed_match.group(1))

    def run_download(self, urls):
        dest = self.download_path.get()
        abs_bin_path = os.path.realpath(self.bin_dir)
        
        cache_dir = os.path.join(abs_bin_path, "cache")
        os.makedirs(cache_dir, exist_ok=True)

        env_vars = os.environ.copy()
        env_vars.pop("PYTHONHOME", None)
        env_vars.pop("PYTHONPATH", None)
        env_vars["XDG_CACHE_HOME"] = cache_dir 
        env_vars["PATH"] = f"{abs_bin_path}{os.pathsep}{env_vars.get('PATH', '')}"

        for url in urls:
            try:
                self.progress_bar.set(0)
                cmd = [
                    self.ytdlp_path, # Run exe directly
                    "--ffmpeg-location", abs_bin_path, 
                    "--cookies-from-browser", self.browser_var.get(),
                    "--js-runtimes", f"node:{self.node_path}",
                    "--remote-components", "ejs:github",
                    "--no-check-certificate",
                    "--force-ipv4",
                    "-o", os.path.join(dest, "%(title)s.%(ext)s"),
                    "--newline",
                    "--progress"
                ]

                cmd += ["--format-sort", "res,quality,br,size"]
                if self.is_playlist_var.get(): cmd.append("--yes-playlist")
                else: cmd.append("--no-playlist")

                mode = self.mode_var.get()
                if mode == "audio_m4a":
                    cmd += ["-f", "bestaudio/best", "--extract-audio", "--audio-format", "m4a"]
                elif mode == "audio_mp3":
                    cmd += ["-f", "bestaudio/best", "--extract-audio", "--audio-format", "mp3", "--audio-quality", "0"]
                else:
                    cmd += ["-f", "bestvideo[height>=1080]+bestaudio/best", "--merge-output-format", "mp4"]

                cmd.append(url.strip())
                
                # Windows specific: Hide console
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                    text=True, encoding="utf-8", env=env_vars, cwd=abs_bin_path, bufsize=1,
                    startupinfo=startupinfo
                )
                
                for line in proc.stdout:
                    clean_line = line.strip()
                    if clean_line:
                        self.log(clean_line)
                        self.update_progress(clean_line)
                        self.update()
                
                proc.wait()
            except Exception as e:
                self.log(f"Error: {e}")
        
        self.progress_bar.set(1)
        self.lbl_status.configure(text="Finished!")
        self.btn_download.configure(state="normal", text="START DOWNLOAD")
        self.log(">>> Selesai!")

if __name__ == "__main__":
    app = YTProApp()
    app.mainloop()