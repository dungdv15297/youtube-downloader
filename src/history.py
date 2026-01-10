"""
Download History Manager Module
Saves and loads download history for persistence across app restarts.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class HistoryItem:
    """Represents a download history entry."""
    url: str
    title: str
    file_path: str
    download_date: str
    status: str  # completed, error
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoryItem':
        return cls(**data)


class DownloadHistory:
    """Manages download history with JSON file persistence."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize history manager.
        
        Args:
            config_dir: Optional custom config directory path
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            appdata = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
            self.config_dir = Path(appdata) / 'YouTubeDownloader'
        
        self.history_file = self.config_dir / 'history.json'
        self._history: List[HistoryItem] = []
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing history
        self._load()
    
    def _load(self) -> None:
        """Load history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._history = [HistoryItem.from_dict(item) for item in data]
            except (json.JSONDecodeError, IOError, KeyError) as e:
                print(f"Warning: Could not load history: {e}")
                self._history = []
    
    def save(self) -> bool:
        """Save history to file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                data = [item.to_dict() for item in self._history]
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving history: {e}")
            return False
    
    def add(self, url: str, title: str, file_path: str, status: str = "completed") -> None:
        """
        Add a new item to history.
        
        Args:
            url: YouTube URL
            title: Video title
            file_path: Path to downloaded file
            status: Download status (completed/error)
        """
        # Check if URL already exists and update it
        for i, item in enumerate(self._history):
            if item.url == url:
                self._history[i] = HistoryItem(
                    url=url,
                    title=title,
                    file_path=file_path,
                    download_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    status=status
                )
                self.save()
                return
        
        # Add new item at the beginning
        self._history.insert(0, HistoryItem(
            url=url,
            title=title,
            file_path=file_path,
            download_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            status=status
        ))
        
        # Limit history to 100 items
        if len(self._history) > 100:
            self._history = self._history[:100]
        
        self.save()
    
    def get_all(self) -> List[HistoryItem]:
        """Get all history items."""
        return self._history.copy()
    
    def clear(self) -> None:
        """Clear all history."""
        self._history = []
        self.save()
    
    def remove(self, url: str) -> None:
        """Remove an item from history by URL."""
        self._history = [item for item in self._history if item.url != url]
        self.save()


# Global history instance
_history_instance: Optional[DownloadHistory] = None


def get_history() -> DownloadHistory:
    """Get the global history instance."""
    global _history_instance
    if _history_instance is None:
        _history_instance = DownloadHistory()
    return _history_instance
