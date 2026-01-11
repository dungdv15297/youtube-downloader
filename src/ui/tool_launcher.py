"""
Tool Launcher UI Module
Main menu window for selecting tools.
"""

import customtkinter as ctk
from typing import Callable, Optional


class ToolCard(ctk.CTkFrame):
    """A clickable card representing a tool."""
    
    def __init__(
        self,
        master,
        icon: str,
        title: str,
        description: str,
        on_click: Callable,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        self.on_click = on_click
        
        # Configure card appearance
        self.configure(
            corner_radius=15,
            border_width=2,
            border_color="#3498db",
            fg_color=("#2c3e50", "#1a252f")
        )
        
        # Make entire card clickable
        self.bind("<Button-1>", self._handle_click)
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
        
        # Content frame
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=20, pady=20)
        self.content.bind("<Button-1>", self._handle_click)
        
        # Icon
        self.icon_label = ctk.CTkLabel(
            self.content,
            text=icon,
            font=ctk.CTkFont(size=48)
        )
        self.icon_label.pack(pady=(10, 15))
        self.icon_label.bind("<Button-1>", self._handle_click)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.content,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.pack(pady=(0, 8))
        self.title_label.bind("<Button-1>", self._handle_click)
        
        # Description
        self.desc_label = ctk.CTkLabel(
            self.content,
            text=description,
            font=ctk.CTkFont(size=12),
            text_color="gray",
            wraplength=200
        )
        self.desc_label.pack()
        self.desc_label.bind("<Button-1>", self._handle_click)
    
    def _handle_click(self, event=None):
        """Handle card click."""
        if self.on_click:
            self.on_click()
    
    def _on_hover(self, event=None):
        """Handle mouse enter."""
        self.configure(border_color="#e74c3c", fg_color=("#34495e", "#253545"))
    
    def _on_leave(self, event=None):
        """Handle mouse leave."""
        self.configure(border_color="#3498db", fg_color=("#2c3e50", "#1a252f"))


class ToolLauncher(ctk.CTk):
    """Main launcher window with tool selection menu."""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("🧰 Tools Hub")
        self.geometry("650x500")
        self.minsize(600, 450)
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Track open tool windows
        self.current_tool_window: Optional[ctk.CTkToplevel] = None
        
        # Build UI
        self._create_widgets()
        
        # Center window
        self._center_window()
    
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
        # Main container
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 30))
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="🧰 Tools Hub",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title_label.pack()
        
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Chọn công cụ bạn muốn sử dụng",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.subtitle_label.pack(pady=(8, 0))
        
        # Tools grid
        self.tools_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.tools_frame.pack(fill="both", expand=True)
        
        # Configure grid
        self.tools_frame.grid_columnconfigure(0, weight=1)
        self.tools_frame.grid_columnconfigure(1, weight=1)
        self.tools_frame.grid_rowconfigure(0, weight=1)
        
        # YouTube Downloader Card
        self.youtube_card = ToolCard(
            self.tools_frame,
            icon="🎬",
            title="YouTube Downloader",
            description="Tải video từ YouTube, Douyin với nhiều định dạng",
            on_click=self._open_youtube_downloader
        )
        self.youtube_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # CapCut Caption Extractor Card
        self.capcut_card = ToolCard(
            self.tools_frame,
            icon="📝",
            title="CapCut Caption",
            description="Trích xuất Caption từ project CapCut ra file SRT/TXT",
            on_click=self._open_capcut_extractor
        )
        self.capcut_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Footer
        self.footer_label = ctk.CTkLabel(
            self.main_frame,
            text="💡 Click vào tool để bắt đầu",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.footer_label.pack(pady=(20, 0))
    
    def _open_youtube_downloader(self):
        """Open YouTube Downloader tool."""
        # Close current tool window if open
        if self.current_tool_window:
            self.current_tool_window.destroy()
        
        # Import and create YouTube Downloader window
        from ui.main_window import YouTubeDownloaderWindow
        self.current_tool_window = YouTubeDownloaderWindow(self, on_back=self._on_tool_close)
        self.current_tool_window.focus()
        
        # Hide launcher
        self.withdraw()
    
    def _open_capcut_extractor(self):
        """Open CapCut Caption Extractor tool."""
        # Close current tool window if open
        if self.current_tool_window:
            self.current_tool_window.destroy()
        
        # Import and create CapCut window
        from ui.capcut_window import CapCutWindow
        self.current_tool_window = CapCutWindow(self, on_back=self._on_tool_close)
        self.current_tool_window.focus()
        
        # Hide launcher
        self.withdraw()
    
    def _on_tool_close(self):
        """Handle tool window close - show launcher again."""
        self.current_tool_window = None
        self.deiconify()
        self.focus()
