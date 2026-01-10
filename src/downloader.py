"""
YouTube Video Downloader Module
Handles video downloading using yt-dlp.
"""

import os
import shutil
import time
import threading
from dataclasses import dataclass
from typing import Callable, Optional
from pathlib import Path

import yt_dlp


@dataclass
class VideoInfo:
    """Contains information about a YouTube video."""
    title: str
    duration: int  # in seconds
    thumbnail_url: str
    uploader: str
    view_count: int
    url: str
    video_id: str
    
    @property
    def duration_str(self) -> str:
        """Get duration as formatted string (HH:MM:SS or MM:SS)."""
        hours, remainder = divmod(self.duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"


@dataclass
class DownloadProgress:
    """Contains download progress information."""
    status: str = 'downloading'
    downloaded_bytes: int = 0
    total_bytes: int = 0
    speed: float = 0
    eta: int = 0
    filename: str = ''
    percent: float = 0
    
    @property
    def speed_str(self) -> str:
        """Get speed as formatted string."""
        if self.speed < 1024:
            return f"{self.speed:.0f} B/s"
        elif self.speed < 1024 * 1024:
            return f"{self.speed / 1024:.1f} KB/s"
        else:
            return f"{self.speed / (1024 * 1024):.1f} MB/s"
    
    @property
    def eta_str(self) -> str:
        """Get ETA as formatted string."""
        if self.eta < 60:
            return f"{self.eta}s"
        minutes, seconds = divmod(self.eta, 60)
        return f"{minutes}m {seconds}s"


class YouTubeDownloader:
    """Downloads YouTube videos using yt-dlp."""
    
    def __init__(self, output_path: str = "."):
        self.output_path = output_path
        self._cancel_flag = False
        self._current_download: Optional[threading.Thread] = None
    
    def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """Get information about a YouTube video without downloading."""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info:
                    return VideoInfo(
                        title=info.get('title', 'Unknown'),
                        duration=info.get('duration', 0),
                        thumbnail_url=info.get('thumbnail', ''),
                        uploader=info.get('uploader', 'Unknown'),
                        view_count=info.get('view_count', 0),
                        url=url,
                        video_id=info.get('id', ''),
                    )
        except Exception as e:
            print(f"Error getting video info: {e}")
        
        return None
    
    def download(
        self,
        url: str,
        output_path: Optional[str] = None,
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None,
        complete_callback: Optional[Callable[[bool, str], None]] = None,
        quality: str = "best",
        download_format: str = "mp4"
    ) -> None:
        """
        Download a YouTube video.
        
        Args:
            url: YouTube video URL
            output_path: Output directory
            progress_callback: Called with progress updates
            complete_callback: Called when download completes
            quality: Video quality (best, 1080p, 720p, 480p)
            download_format: Format (mp4, mp3, mp4_video)
        """
        self._cancel_flag = False
        output_dir = output_path or self.output_path
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        def progress_hook(d):
            if self._cancel_flag:
                raise Exception("Download cancelled")
            
            if d['status'] == 'downloading' and progress_callback:
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                speed = d.get('speed', 0)
                eta = d.get('eta', 0)
                
                percent = (downloaded / total * 100) if total > 0 else 0
                
                progress = DownloadProgress(
                    percent=percent,
                    speed=speed or 0,
                    eta=eta or 0,
                    downloaded_bytes=downloaded,
                    total_bytes=total
                )
                progress_callback(progress)
        
        has_ffmpeg = shutil.which("ffmpeg") is not None
        timestamp = int(time.time() * 1000)
        
        # Configure based on download format
        if download_format == "mp3":
            # Audio only - extract to MP3
            if has_ffmpeg:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(output_dir, f'%(title)s_{timestamp}.%(ext)s'),
                    'progress_hooks': [progress_hook],
                    'quiet': True,
                    'no_warnings': True,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
            else:
                ydl_opts = {
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',
                    'outtmpl': os.path.join(output_dir, f'%(title)s_{timestamp}.%(ext)s'),
                    'progress_hooks': [progress_hook],
                    'quiet': True,
                    'no_warnings': True,
                }
                
        elif download_format == "mp4_video":
            # Video only (no audio)
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]/bestvideo/best',
                'outtmpl': os.path.join(output_dir, f'%(title)s_{timestamp}.%(ext)s'),
                'progress_hooks': [progress_hook],
                'quiet': True,
                'no_warnings': True,
            }
            
        else:
            # mp4 - Video + Audio (default)
            if has_ffmpeg:
                if quality == "1080p":
                    format_str = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]'
                elif quality == "720p":
                    format_str = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]'
                elif quality == "480p":
                    format_str = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best[height<=480]'
                else:
                    format_str = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best[ext=mp4]/best'
                
                ydl_opts = {
                    'format': format_str,
                    'outtmpl': os.path.join(output_dir, f'%(title)s_{timestamp}.%(ext)s'),
                    'progress_hooks': [progress_hook],
                    'quiet': True,
                    'no_warnings': True,
                    'merge_output_format': 'mp4',
                }
            else:
                if quality == "1080p":
                    format_str = 'best[height<=1080][ext=mp4]/best[height<=1080]/best'
                elif quality == "720p":
                    format_str = 'best[height<=720][ext=mp4]/best[height<=720]/best'
                elif quality == "480p":
                    format_str = 'best[height<=480][ext=mp4]/best[height<=480]/best'
                else:
                    format_str = 'best[ext=mp4]/best'
                
                ydl_opts = {
                    'format': format_str,
                    'outtmpl': os.path.join(output_dir, f'%(title)s_{timestamp}.%(ext)s'),
                    'progress_hooks': [progress_hook],
                    'quiet': True,
                    'no_warnings': True,
                }
        
        def do_download():
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                if complete_callback:
                    complete_callback(True, "Tải thành công!")
            except Exception as e:
                error_msg = str(e)
                if "cancelled" in error_msg.lower():
                    error_msg = "Đã hủy tải xuống"
                if complete_callback:
                    complete_callback(False, f"Lỗi: {error_msg}")
        
        self._current_download = threading.Thread(target=do_download, daemon=True)
        self._current_download.start()
    
    def cancel(self) -> None:
        """Cancel the current download."""
        self._cancel_flag = True
    
    def is_downloading(self) -> bool:
        """Check if a download is in progress."""
        return self._current_download is not None and self._current_download.is_alive()
