"""
YouTube URL Validator Module
Validates if a given URL is a valid YouTube video URL.
"""

import re
from typing import Optional, Tuple


class YouTubeValidator:
    """Validates YouTube URLs and extracts video IDs."""
    
    # Regex patterns for different YouTube URL formats
    PATTERNS = [
        # Standard watch URL: https://www.youtube.com/watch?v=VIDEO_ID
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
        # Short URL: https://youtu.be/VIDEO_ID
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        # Shorts URL: https://www.youtube.com/shorts/VIDEO_ID
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
        # Embed URL: https://www.youtube.com/embed/VIDEO_ID
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        # Mobile URL: https://m.youtube.com/watch?v=VIDEO_ID
        r'(?:https?://)?m\.youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    @classmethod
    def is_youtube_url(cls, url: str) -> bool:
        """
        Check if the given URL is a valid YouTube URL.
        
        Args:
            url: The URL string to validate
            
        Returns:
            True if the URL is a valid YouTube URL, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        url = url.strip()
        
        for pattern in cls.PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        return False
    
    @classmethod
    def extract_video_id(cls, url: str) -> Optional[str]:
        """
        Extract the video ID from a YouTube URL.
        
        Args:
            url: The YouTube URL
            
        Returns:
            The 11-character video ID, or None if not found
        """
        if not url or not isinstance(url, str):
            return None
        
        url = url.strip()
        
        for pattern in cls.PATTERNS:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    @classmethod
    def validate_and_extract(cls, url: str) -> Tuple[bool, Optional[str], str]:
        """
        Validate URL and extract video ID in one call.
        
        Args:
            url: The URL to validate
            
        Returns:
            Tuple of (is_valid, video_id, message)
        """
        if not url or not isinstance(url, str):
            return False, None, "URL không được để trống"
        
        url = url.strip()
        
        if not url:
            return False, None, "URL không được để trống"
        
        video_id = cls.extract_video_id(url)
        
        if video_id:
            return True, video_id, "URL YouTube hợp lệ"
        else:
            return False, None, "Đây không phải URL YouTube hợp lệ"


# Convenience functions
def is_youtube_url(url: str) -> bool:
    """Check if URL is a valid YouTube URL."""
    return YouTubeValidator.is_youtube_url(url)


def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from YouTube URL."""
    return YouTubeValidator.extract_video_id(url)
