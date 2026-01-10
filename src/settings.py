"""
Settings Management Module
Handles saving and loading application settings.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class Settings:
    """Manages application settings with JSON file persistence."""
    
    DEFAULT_SETTINGS = {
        "download_folder": None,  # Will be set to default Downloads/YouTube
        "video_quality": "best",  # best, 1080p, 720p, 480p
        "theme": "dark",  # dark, light
        "window_geometry": None,  # Window size and position
    }
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize settings manager.
        
        Args:
            config_dir: Optional custom config directory path
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Use AppData/Local for Windows
            appdata = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
            self.config_dir = Path(appdata) / 'YouTubeDownloader'
        
        self.config_file = self.config_dir / 'settings.json'
        self._settings: Dict[str, Any] = {}
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing settings or create defaults
        self._load()
    
    def _get_default_download_folder(self) -> str:
        """Get the default download folder path."""
        downloads = Path.home() / 'Downloads' / 'YouTube'
        downloads.mkdir(parents=True, exist_ok=True)
        return str(downloads)
    
    def _load(self) -> None:
        """Load settings from config file."""
        self._settings = self.DEFAULT_SETTINGS.copy()
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    self._settings.update(saved_settings)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load settings: {e}")
        
        # Set default download folder if not set
        if not self._settings.get("download_folder"):
            self._settings["download_folder"] = self._get_default_download_folder()
    
    def save(self) -> bool:
        """
        Save current settings to config file.
        
        Returns:
            True if save was successful, False otherwise
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.
        
        Args:
            key: Setting key
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        return self._settings.get(key, default)
    
    def set(self, key: str, value: Any, auto_save: bool = True) -> None:
        """
        Set a setting value.
        
        Args:
            key: Setting key
            value: Value to set
            auto_save: Whether to automatically save after setting
        """
        self._settings[key] = value
        if auto_save:
            self.save()
    
    @property
    def download_folder(self) -> str:
        """Get the download folder path."""
        folder = self.get("download_folder")
        if not folder:
            folder = self._get_default_download_folder()
            self.set("download_folder", folder)
        
        # Ensure folder exists
        Path(folder).mkdir(parents=True, exist_ok=True)
        return folder
    
    @download_folder.setter
    def download_folder(self, path: str) -> None:
        """Set the download folder path."""
        Path(path).mkdir(parents=True, exist_ok=True)
        self.set("download_folder", path)
    
    @property
    def video_quality(self) -> str:
        """Get video quality setting."""
        return self.get("video_quality", "best")
    
    @video_quality.setter
    def video_quality(self, quality: str) -> None:
        """Set video quality."""
        self.set("video_quality", quality)
    
    @property
    def theme(self) -> str:
        """Get theme setting."""
        return self.get("theme", "dark")
    
    @theme.setter
    def theme(self, theme: str) -> None:
        """Set theme."""
        self.set("theme", theme)


# Global settings instance
_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
