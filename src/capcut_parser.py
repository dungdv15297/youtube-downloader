"""
CapCut Draft Parser Module
Parses CapCut draft_content.json files to extract captions.
"""

import json
import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CaptionItem:
    """Represents a single caption/subtitle item."""
    text: str
    start_time: float  # in seconds
    end_time: float    # in seconds


class CapCutParser:
    """Parser for CapCut draft_content.json files."""
    
    @staticmethod
    def find_draft_file(folder_path: str) -> Optional[str]:
        """
        Find draft_content.json in a folder.
        Searches recursively for the file.
        """
        if os.path.isfile(folder_path):
            if folder_path.endswith('.json'):
                return folder_path
            return None
        
        for root, dirs, files in os.walk(folder_path):
            if 'draft_content.json' in files:
                return os.path.join(root, 'draft_content.json')
        return None
    
    @staticmethod
    def parse_draft(file_path: str) -> List[CaptionItem]:
        """
        Parse a CapCut draft_content.json file and extract captions.
        
        Args:
            file_path: Path to draft_content.json
            
        Returns:
            List of CaptionItem objects
        """
        captions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
            raise ValueError(f"Không thể đọc file: {e}")
        
        # CapCut stores tracks in different structures depending on version
        # Common locations for text/caption data:
        # 1. materials.texts (newer versions)
        # 2. tracks with type "text" or "sticker"
        
        materials = data.get('materials', {})
        tracks = data.get('tracks', [])
        texts = materials.get('texts', [])
        
        # Build a lookup map of text materials by ID
        text_map = {}
        for text_item in texts:
            text_id = text_item.get('id', '')
            content = text_item.get('content', '')
            actual_text = CapCutParser._extract_text_from_content(content)
            if text_id and actual_text:
                text_map[text_id] = actual_text
        
        # Parse from tracks to get timing and match with text materials
        for track in tracks:
            track_type = track.get('type', '')
            segments = track.get('segments', [])
            
            for segment in segments:
                # Get timing info (in microseconds typically)
                target_timerange = segment.get('target_timerange', {})
                start_us = target_timerange.get('start', 0)
                duration_us = target_timerange.get('duration', 0)
                
                # Convert to seconds (CapCut uses microseconds)
                start_sec = start_us / 1000000.0
                duration_sec = duration_us / 1000000.0
                end_sec = start_sec + duration_sec
                
                # Get text content via material_id
                material_id = segment.get('material_id', '')
                
                if material_id and material_id in text_map:
                    captions.append(CaptionItem(
                        text=text_map[material_id],
                        start_time=start_sec,
                        end_time=end_sec
                    ))
                    # Remove from map to avoid duplicates
                    del text_map[material_id]
        
        # Add any remaining texts without timing (fallback)
        for text_id, text_content in text_map.items():
            captions.append(CaptionItem(
                text=text_content,
                start_time=0,
                end_time=0
            ))
        
        # Method 3: Check for stickers with text
        stickers = materials.get('stickers', [])
        for sticker in stickers:
            # Some stickers contain text content
            text = sticker.get('text', '')
            actual_text = CapCutParser._extract_text_from_content(text) if text else ''
            if actual_text:
                captions.append(CaptionItem(
                    text=actual_text,
                    start_time=0,
                    end_time=0
                ))
        
        # Method 4: Deep search for any text content
        if not captions:
            captions = CapCutParser._deep_search_texts(data)
        
        # Sort by start time
        captions.sort(key=lambda x: x.start_time)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_captions = []
        for cap in captions:
            if cap.text not in seen and cap.text.strip():
                seen.add(cap.text)
                unique_captions.append(cap)
        
        return unique_captions
    
    @staticmethod
    def _extract_text_from_content(content) -> str:
        """
        Extract pure text from CapCut content field.
        Content may be plain text or JSON with styles.
        
        Example JSON format:
        {"styles":[...],"text":"实际文本内容"}
        """
        if not content:
            return ""
        
        if not isinstance(content, str):
            return str(content)
        
        # Try to parse as JSON (CapCut stores styled text as JSON)
        content = content.strip()
        if content.startswith('{') and content.endswith('}'):
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    # Get the 'text' field which contains the actual caption
                    return data.get('text', '')
            except json.JSONDecodeError:
                pass
        
        # If not JSON or parsing failed, return as-is (plain text)
        return content
    
    @staticmethod
    def _deep_search_texts(data, depth=0, max_depth=10) -> List[CaptionItem]:
        """Recursively search for text content in nested structures."""
        captions = []
        
        if depth > max_depth:
            return captions
        
        if isinstance(data, dict):
            # Check for text-like keys
            for key in ['content', 'text', 'recognized_text', 'words']:
                if key in data:
                    value = data[key]
                    if isinstance(value, str) and len(value.strip()) > 0:
                        # Try to get timing
                        start = data.get('start', 0)
                        duration = data.get('duration', 0)
                        if isinstance(start, (int, float)) and start > 1000:
                            start = start / 1000000
                        if isinstance(duration, (int, float)) and duration > 1000:
                            duration = duration / 1000000
                        
                        captions.append(CaptionItem(
                            text=value.strip(),
                            start_time=start,
                            end_time=start + duration
                        ))
                    elif isinstance(value, list):
                        # Handle word-level data
                        for item in value:
                            if isinstance(item, dict):
                                word = item.get('word', '') or item.get('text', '')
                                if word:
                                    captions.append(CaptionItem(
                                        text=word,
                                        start_time=0,
                                        end_time=0
                                    ))
            
            # Recurse into nested dicts
            for v in data.values():
                captions.extend(CapCutParser._deep_search_texts(v, depth + 1, max_depth))
        
        elif isinstance(data, list):
            for item in data:
                captions.extend(CapCutParser._deep_search_texts(item, depth + 1, max_depth))
        
        return captions
    
    @staticmethod
    def to_srt(captions: List[CaptionItem]) -> str:
        """
        Convert captions to SRT format.
        
        SRT format (with CRLF line endings for compatibility):
        1
        00:00:01,000 --> 00:00:04,000
        Caption text here
        
        2
        00:00:04,500 --> 00:00:08,000
        Another caption
        """
        lines = []
        
        for i, cap in enumerate(captions, 1):
            start = CapCutParser._format_srt_time(cap.start_time)
            end = CapCutParser._format_srt_time(cap.end_time)
            
            lines.append(str(i))
            lines.append(f"{start} --> {end}")
            lines.append(cap.text)
            lines.append("")  # Empty line between entries
        
        # Use CRLF line endings for Windows/CapCut compatibility
        return "\r\n".join(lines)
    
    @staticmethod
    def _format_srt_time(seconds: float) -> str:
        """Format seconds to SRT time format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    @staticmethod
    def to_txt(captions: List[CaptionItem]) -> str:
        """Convert captions to plain text (one line per caption)."""
        return "\n".join(cap.text for cap in captions if cap.text.strip())
    
    @staticmethod
    def to_txt_with_timing(captions: List[CaptionItem]) -> str:
        """Convert captions to text with timing info."""
        lines = []
        for cap in captions:
            if cap.text.strip():
                start = CapCutParser._format_srt_time(cap.start_time)
                lines.append(f"[{start}] {cap.text}")
        return "\n".join(lines)
