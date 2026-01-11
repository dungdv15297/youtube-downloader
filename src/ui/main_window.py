"""
Main Window UI Module
The main application window with paste button and animated download queue.
"""

import os
import shutil
import subprocess
import threading
import pyperclip
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum
import time

from validator import YouTubeValidator
from downloader import YouTubeDownloader, VideoInfo, DownloadProgress
from settings import get_settings
from history import get_history, DownloadHistory


class DownloadStatus(Enum):
    """Status of a download item."""
    LOADING = "loading"      # Getting video info (yellow glow)
    DOWNLOADING = "downloading"  # Downloading (blue glow)
    COMPLETED = "completed"  # Done (green glow)
    ERROR = "error"          # Error (red)


@dataclass
class DownloadItem:
    """Represents a video download in the queue."""
    url: str
    title: str = ""
    status: DownloadStatus = DownloadStatus.LOADING
    progress: float = 0.0
    file_path: str = ""
    error_message: str = ""


class AnimatedDownloadCard(ctk.CTkFrame):
    """A card showing download status with animated border glow."""
    
    COLORS = {
        DownloadStatus.LOADING: ("#f1c40f", "#f39c12"),      # Yellow
        DownloadStatus.DOWNLOADING: ("#3498db", "#2980b9"),  # Blue
        DownloadStatus.COMPLETED: ("#2ecc71", "#27ae60"),    # Green
        DownloadStatus.ERROR: ("#e74c3c", "#c0392b"),        # Red
    }
    
    def __init__(self, master, item: DownloadItem, on_open_click=None, on_open_folder_click=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.item = item
        self.on_open_click = on_open_click
        self.on_open_folder_click = on_open_folder_click
        self._glow_phase = 0
        self._animating = False
        
        self.configure(corner_radius=10, border_width=3)
        self._update_border_color()
        
        # Main content
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=8)
        
        # Left side - Video info
        self.info_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.info_frame.pack(side="left", fill="both", expand=True)
        
        self.title_label = ctk.CTkLabel(
            self.info_frame,
            text=item.title or "Đang tải thông tin...",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
            wraplength=300
        )
        self.title_label.pack(fill="x", anchor="w")
        
        self.url_label = ctk.CTkLabel(
            self.info_frame,
            text=self._truncate_url(item.url),
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="w"
        )
        self.url_label.pack(fill="x", anchor="w")
        
        # Right side - Status and actions
        self.action_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.action_frame.pack(side="right", padx=(10, 0))
        
        self.status_label = ctk.CTkLabel(
            self.action_frame,
            text="⏳ Đang tải...",
            font=ctk.CTkFont(size=11),
            width=120
        )
        self.status_label.pack()
        
        # Buttons frame (hidden initially)
        self.buttons_frame = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        
        self.open_btn = ctk.CTkButton(
            self.buttons_frame,
            text="▶️ Mở",
            font=ctk.CTkFont(size=10),
            width=55,
            height=26,
            corner_radius=5,
            command=self._on_open,
            fg_color="#27ae60",
            hover_color="#1e8449"
        )
        self.open_btn.pack(side="left", padx=(0, 5))
        
        self.folder_btn = ctk.CTkButton(
            self.buttons_frame,
            text="📁",
            font=ctk.CTkFont(size=12),
            width=35,
            height=26,
            corner_radius=5,
            command=self._on_open_folder,
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        self.folder_btn.pack(side="left")
        
        self._start_animation()
    
    def _truncate_url(self, url: str, max_length: int = 50) -> str:
        """Truncate URL for display."""
        if len(url) <= max_length:
            return url
        return url[:max_length - 3] + "..."
    
    def _update_border_color(self):
        """Update border color based on status."""
        colors = self.COLORS.get(self.item.status, ("#666", "#444"))
        self.configure(border_color=colors[0])
    
    def _start_animation(self):
        """Start border glow animation."""
        if self.item.status in [DownloadStatus.LOADING, DownloadStatus.DOWNLOADING]:
            self._animating = True
            self._animate_glow()
    
    def _stop_animation(self):
        """Stop border animation."""
        self._animating = False
    
    def _animate_glow(self):
        """Animate border glow effect."""
        if not self._animating:
            return
        
        colors = self.COLORS.get(self.item.status, ("#666", "#444"))
        # Pulse between two shades
        self._glow_phase = (self._glow_phase + 1) % 20
        if self._glow_phase < 10:
            self.configure(border_color=colors[0])
        else:
            self.configure(border_color=colors[1])
        
        self.after(100, self._animate_glow)
    
    def update_status(self, status: DownloadStatus, title: str = None, progress: float = None, file_path: str = None, error: str = None):
        """Update the card status and appearance."""
        old_status = self.item.status
        self.item.status = status
        
        if title:
            self.item.title = title
            self.title_label.configure(text=title)
        
        if progress is not None:
            self.item.progress = progress
        
        if file_path:
            self.item.file_path = file_path
        
        if error:
            self.item.error_message = error
        
        # Update UI based on status
        if status == DownloadStatus.LOADING:
            self.status_label.configure(text="⏳ Đang tải...")
            self.buttons_frame.pack_forget()
        elif status == DownloadStatus.DOWNLOADING:
            progress_text = f"⬇️ {self.item.progress:.0f}%"
            self.status_label.configure(text=progress_text)
            self.buttons_frame.pack_forget()
        elif status == DownloadStatus.COMPLETED:
            self.status_label.configure(text="✅ Hoàn thành")
            self.buttons_frame.pack(pady=(5, 0))
            self._stop_animation()
            # Flash green effect
            self._flash_complete()
        elif status == DownloadStatus.ERROR:
            self.status_label.configure(text=f"❌ Lỗi")
            self.buttons_frame.pack_forget()
            self._stop_animation()
        
        self._update_border_color()
        
        # Start/stop animation based on status change
        if old_status != status:
            if status in [DownloadStatus.LOADING, DownloadStatus.DOWNLOADING]:
                self._animating = True
                self._animate_glow()
    
    def _flash_complete(self):
        """Flash green when download completes."""
        def flash(count):
            if count <= 0:
                return
            current = self.cget("border_color")
            new_color = "#2ecc71" if current != "#2ecc71" else "#27ae60"
            self.configure(border_color=new_color)
            self.after(150, lambda: flash(count - 1))
        flash(6)
    
    def _on_open(self):
        """Handle open button click."""
        if self.on_open_click and self.item.file_path:
            self.on_open_click(self.item.file_path)
    
    def _on_open_folder(self):
        """Handle open folder button click."""
        if self.on_open_folder_click and self.item.file_path:
            self.on_open_folder_click(self.item.file_path)


class YouTubeDownloaderWindow(ctk.CTkToplevel):
    """YouTube Downloader tool window."""
    
    def __init__(self, master=None, on_back=None):
        super().__init__(master)
        
        self.on_back = on_back
        
        # Settings
        self.settings = get_settings()
        
        # History
        self.history = get_history()
        
        # Configure window
        self.title("🎬 YouTube Downloader")
        self.geometry("600x700")
        self.minsize(550, 650)
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Initialize downloader
        self.downloader = YouTubeDownloader(self.settings.download_folder)
        self.download_cards: Dict[str, AnimatedDownloadCard] = {}
        
        # Build UI
        self._create_widgets()
        
        # Check FFmpeg status
        self._check_ffmpeg_status()
        
        # Load download history
        self._load_history()
        
        # Center window
        self._center_window()
    
    def _on_close(self):
        """Handle window close."""
        if self.on_back:
            self.on_back()
        self.destroy()
    
    def _center_window(self):
        """Center the window on screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_widgets(self):
        """Create all UI widgets."""
        # Main container with padding
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # === Header ===
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 15))
        
        # Back button (only if launched from launcher)
        if self.on_back:
            self.back_btn = ctk.CTkButton(
                self.header_frame,
                text="← Quay lại",
                font=ctk.CTkFont(size=11),
                width=90,
                height=28,
                corner_radius=6,
                command=self._on_close,
                fg_color="#7f8c8d",
                hover_color="#636e72"
            )
            self.back_btn.pack(side="left", padx=(0, 10))
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="🎬 YouTube Downloader",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(side="left")
        
        # FFmpeg status/install button
        self.ffmpeg_btn = ctk.CTkButton(
            self.header_frame,
            text="⚙️ Kiểm tra...",
            font=ctk.CTkFont(size=11),
            width=110,
            height=28,
            corner_radius=6,
            command=self._on_install_ffmpeg,
            fg_color="#9b59b6",
            hover_color="#8e44ad"
        )
        self.ffmpeg_btn.pack(side="right")
        
        # === Folder Selection ===
        self.folder_frame = ctk.CTkFrame(self.main_frame)
        self.folder_frame.pack(fill="x", pady=(0, 15))
        
        self.folder_title = ctk.CTkLabel(
            self.folder_frame,
            text="📁 Thư mục lưu video:",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        self.folder_title.pack(fill="x", padx=12, pady=(10, 5))
        
        self.folder_inner_frame = ctk.CTkFrame(self.folder_frame, fg_color="transparent")
        self.folder_inner_frame.pack(fill="x", padx=12, pady=(0, 10))
        
        self.folder_path_label = ctk.CTkLabel(
            self.folder_inner_frame,
            text=self.settings.download_folder,
            font=ctk.CTkFont(size=10),
            text_color="#3498db",
            anchor="w",
            wraplength=380
        )
        self.folder_path_label.pack(side="left", fill="x", expand=True)
        
        self.change_folder_btn = ctk.CTkButton(
            self.folder_inner_frame,
            text="📂 Đổi",
            font=ctk.CTkFont(size=11),
            width=70,
            height=28,
            corner_radius=6,
            command=self._on_change_folder,
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        self.change_folder_btn.pack(side="right")
        
        # === Format Selection ===
        self.format_frame = ctk.CTkFrame(self.main_frame)
        self.format_frame.pack(fill="x", pady=(0, 15))
        
        self.format_label = ctk.CTkLabel(
            self.format_frame,
            text="🎬 Định dạng tải:",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        self.format_label.pack(side="left", padx=12, pady=10)
        
        self.format_var = ctk.StringVar(value="mp4")
        self.format_selector = ctk.CTkSegmentedButton(
            self.format_frame,
            values=["mp4", "mp3", "mp4_video"],
            variable=self.format_var,
            font=ctk.CTkFont(size=11),
            command=self._on_format_change
        )
        self.format_selector.pack(side="right", padx=12, pady=10)
        
        # Format descriptions
        self.format_desc = ctk.CTkLabel(
            self.format_frame,
            text="Video + Audio",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.format_desc.pack(side="right", padx=(0, 10), pady=10)
        
        # === Paste Link Button ===
        self.paste_btn = ctk.CTkButton(
            self.main_frame,
            text="📋  PASTE LINK VÀ TẢI",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            corner_radius=10,
            command=self._on_paste_click,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        self.paste_btn.pack(fill="x", pady=(0, 15))
        
        # === Download Queue Label ===
        self.queue_label = ctk.CTkLabel(
            self.main_frame,
            text="📥 Danh sách tải xuống:",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        self.queue_label.pack(fill="x", pady=(5, 10))
        
        # === Download Queue (Scrollable) ===
        self.queue_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color="transparent",
            corner_radius=10
        )
        self.queue_frame.pack(fill="both", expand=True)
        
        # Empty state message
        self.empty_label = ctk.CTkLabel(
            self.queue_frame,
            text="💡 Copy link YouTube và nhấn 'PASTE LINK VÀ TẢI' để bắt đầu",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.empty_label.pack(pady=30)
        
        # === Status Bar ===
        self.status_frame = ctk.CTkFrame(self.main_frame, height=30)
        self.status_frame.pack(fill="x", pady=(10, 0))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Sẵn sàng",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.status_label.pack(side="left", padx=10, pady=5)
    
    def _is_ffmpeg_installed(self) -> bool:
        """Check if FFmpeg is installed and available in PATH."""
        return shutil.which("ffmpeg") is not None
    
    def _check_ffmpeg_status(self):
        """Check FFmpeg installation status and update UI."""
        if self._is_ffmpeg_installed():
            self.ffmpeg_btn.configure(
                text="✅ FFmpeg OK",
                fg_color="#27ae60",
                hover_color="#27ae60",
                state="disabled"
            )
        else:
            self.ffmpeg_btn.configure(
                text="⚙️ Cài FFmpeg",
                fg_color="#9b59b6",
                hover_color="#8e44ad",
                state="normal"
            )
    
    def _on_format_change(self, value: str):
        """Handle format selection change."""
        descriptions = {
            "mp4": "Video + Audio",
            "mp3": "Chỉ Audio",
            "mp4_video": "Chỉ Video"
        }
        self.format_desc.configure(text=descriptions.get(value, ""))
    
    def _load_history(self):
        """Load download history and display as completed cards."""
        history_items = self.history.get_all()
        
        if not history_items:
            return
        
        # Hide empty state
        self.empty_label.pack_forget()
        
        # Create cards for each history item
        for hist_item in history_items:
            if hist_item.url in self.download_cards:
                continue
            
            # Create download item with completed status
            item = DownloadItem(
                url=hist_item.url,
                title=hist_item.title,
                status=DownloadStatus.COMPLETED,
                file_path=hist_item.file_path
            )
            
            # Create card
            card = AnimatedDownloadCard(
                self.queue_frame,
                item,
                on_open_click=self._open_file,
                on_open_folder_click=self._open_folder
            )
            card.pack(fill="x", pady=(0, 10))
            
            # Mark as completed immediately (no animation)
            card.update_status(
                DownloadStatus.COMPLETED,
                title=hist_item.title,
                file_path=hist_item.file_path
            )
            
            self.download_cards[hist_item.url] = card
    
    def _on_paste_click(self):
        """Handle paste button click - paste URL and start download immediately."""
        try:
            clipboard_content = pyperclip.paste()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc clipboard: {e}")
            return
        
        if not clipboard_content:
            messagebox.showwarning("Cảnh báo", "Clipboard trống! Hãy copy một URL YouTube trước.")
            return
        
        url = clipboard_content.strip()
        
        # Validate URL
        is_valid, video_id, message = YouTubeValidator.validate_and_extract(url)
        
        if not is_valid:
            messagebox.showwarning("URL không hợp lệ", f"{message}\n\nHãy copy một link YouTube hợp lệ.")
            return
        
        # Generate unique key for this download (allows same URL multiple times)
        download_key = f"{url}_{int(time.time() * 1000)}"
        
        # Hide empty state
        self.empty_label.pack_forget()
        
        # Create download item
        item = DownloadItem(url=url)
        
        # Create animated card - pack at top (before=existing cards)
        card = AnimatedDownloadCard(
            self.queue_frame,
            item,
            on_open_click=self._open_file,
            on_open_folder_click=self._open_folder
        )
        # Pack at beginning to show new downloads at top
        for widget in self.queue_frame.winfo_children():
            widget.pack_forget()
        card.pack(fill="x", pady=(0, 10))
        # Re-pack existing cards below
        for key, existing_card in self.download_cards.items():
            existing_card.pack(fill="x", pady=(0, 10))
        
        self.download_cards[download_key] = card
        self.status_label.configure(text="🔍 Đang lấy thông tin video...")
        
        # Get video info in background
        def fetch_and_download():
            try:
                info = self.downloader.get_video_info(url)
                if info:
                    self.after(0, lambda: self._start_download(card, url, info))
                else:
                    self.after(0, lambda: self._handle_error_card(card, "Không thể lấy thông tin video"))
            except Exception as e:
                self.after(0, lambda: self._handle_error_card(card, str(e)))
        
        threading.Thread(target=fetch_and_download, daemon=True).start()
    
    def _start_download(self, card: AnimatedDownloadCard, url: str, info: VideoInfo):
        """Start downloading a video after getting info."""
        card.update_status(DownloadStatus.DOWNLOADING, title=info.title, progress=0)
        self.status_label.configure(text=f"⬇️ Đang tải: {info.title[:30]}...")
        
        def on_progress(progress: DownloadProgress):
            self.after(0, lambda: card.update_status(
                DownloadStatus.DOWNLOADING,
                progress=progress.percent
            ))
        
        def on_complete(success: bool, message: str):
            if success:
                # Find the downloaded file
                file_path = os.path.join(self.settings.download_folder, f"{info.title}.mp4")
                # Try common extensions
                for ext in ['.mp4', '.webm', '.mkv']:
                    potential_path = os.path.join(self.settings.download_folder, f"{info.title}{ext}")
                    if os.path.exists(potential_path):
                        file_path = potential_path
                        break
                
                # Save to history
                self.history.add(
                    url=url,
                    title=info.title,
                    file_path=file_path,
                    status="completed"
                )
                
                self.after(0, lambda: card.update_status(
                    DownloadStatus.COMPLETED,
                    file_path=file_path
                ))
                self.after(0, lambda: self.status_label.configure(text=f"✅ Hoàn thành: {info.title[:30]}"))
            else:
                self.after(0, lambda: self._handle_error_card(card, message))
        
        self.downloader.download(
            url=url,
            output_path=self.settings.download_folder,
            progress_callback=on_progress,
            complete_callback=on_complete,
            quality=self.settings.video_quality,
            download_format=self.format_var.get()  # mp4, mp3, or mp4_video
        )
    
    def _handle_error_card(self, card: AnimatedDownloadCard, error_message: str):
        """Handle download error for a specific card."""
        card.update_status(DownloadStatus.ERROR, error=error_message)
        self.status_label.configure(text=f"❌ Lỗi: {error_message[:50]}")
    
    def _open_file(self, file_path: str):
        """Open downloaded file."""
        if os.path.exists(file_path):
            os.startfile(file_path)
        else:
            # Open folder instead if file not found
            self._open_folder(file_path)
    
    def _open_folder(self, file_path: str):
        """Open folder containing the file."""
        folder = os.path.dirname(file_path)
        if os.path.exists(folder):
            os.startfile(folder)
        elif os.path.exists(self.settings.download_folder):
            os.startfile(self.settings.download_folder)
    
    def _on_change_folder(self):
        """Handle change folder button click."""
        folder = filedialog.askdirectory(
            title="Chọn thư mục lưu video",
            initialdir=self.settings.download_folder
        )
        
        if folder:
            self.settings.download_folder = folder
            self.downloader.output_path = folder
            self.folder_path_label.configure(text=folder)
            self.status_label.configure(text=f"📁 Đã đổi thư mục")
    
    def _on_install_ffmpeg(self):
        """Handle install FFmpeg button click."""
        if messagebox.askyesno(
            "Cài đặt FFmpeg",
            "FFmpeg cần thiết để tải video chất lượng cao.\n\n"
            "Bạn có muốn cài đặt FFmpeg không?\n"
            "(Cần kết nối Internet)"
        ):
            self.ffmpeg_btn.configure(state="disabled", text="⏳ Đang cài...")
            self.status_label.configure(text="🔧 Đang cài đặt FFmpeg...")
            self.update()
            
            def install():
                try:
                    # Install via winget
                    result = subprocess.run(
                        ["winget", "install", "-e", "--id", "Gyan.FFmpeg", "--accept-source-agreements", "--accept-package-agreements"],
                        capture_output=True,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    # Find FFmpeg location and add to PATH
                    ffmpeg_bin_path = self._find_ffmpeg_path()
                    
                    if ffmpeg_bin_path:
                        self._add_to_path(ffmpeg_bin_path)
                        self.after(0, lambda: self._ffmpeg_install_complete(True, "FFmpeg đã được cài đặt!"))
                    elif result.returncode == 0 or "already installed" in result.stdout.lower():
                        self.after(0, lambda: self._ffmpeg_install_complete(True, "FFmpeg đã cài. Vui lòng khởi động lại app."))
                    else:
                        self.after(0, lambda: self._ffmpeg_install_complete(False, f"Lỗi: {result.stderr or result.stdout}"))
                        
                except FileNotFoundError:
                    self.after(0, lambda: self._ffmpeg_install_complete(
                        False, 
                        "winget không khả dụng. Tải FFmpeg từ ffmpeg.org"
                    ))
                except Exception as e:
                    self.after(0, lambda: self._ffmpeg_install_complete(False, str(e)))
            
            threading.Thread(target=install, daemon=True).start()
    
    def _find_ffmpeg_path(self) -> Optional[str]:
        """Find FFmpeg installation path."""
        search_paths = [
            r"C:\ffmpeg\bin",
            r"C:\Program Files\FFmpeg\bin",
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links"),
        ]
        
        # Check WinGet packages
        winget_packages = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages")
        if os.path.exists(winget_packages):
            for folder in os.listdir(winget_packages):
                if "FFmpeg" in folder:
                    folder_path = os.path.join(winget_packages, folder)
                    for root, dirs, files in os.walk(folder_path):
                        if "ffmpeg.exe" in files:
                            return root
        
        for path in search_paths:
            if os.path.exists(path) and os.path.exists(os.path.join(path, "ffmpeg.exe")):
                return path
        
        return None
    
    def _add_to_path(self, ffmpeg_path: str):
        """Add FFmpeg to PATH."""
        current_path = os.environ.get("PATH", "")
        if ffmpeg_path.lower() not in current_path.lower():
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ)
                user_path, _ = winreg.QueryValueEx(key, "Path")
                winreg.CloseKey(key)
            except:
                user_path = ""
            
            if ffmpeg_path.lower() not in user_path.lower():
                new_path = f"{user_path};{ffmpeg_path}" if user_path else ffmpeg_path
                subprocess.run(["setx", "PATH", new_path], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            os.environ["PATH"] = f"{current_path};{ffmpeg_path}"
    
    def _ffmpeg_install_complete(self, success: bool, message: str):
        """Handle FFmpeg installation completion."""
        if success:
            self.status_label.configure(text=f"✅ {message}")
            self._check_ffmpeg_status()
            messagebox.showinfo("Thành công", message)
        else:
            self.ffmpeg_btn.configure(state="normal", text="⚙️ Cài FFmpeg")
            self.status_label.configure(text=f"❌ {message}")
            messagebox.showerror("Lỗi", message)
