"""
CapCut Caption Extractor Window
UI for extracting captions from CapCut projects.
"""

import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Callable, Optional, List

from capcut_parser import CapCutParser, CaptionItem


class CapCutWindow(ctk.CTkToplevel):
    """Window for CapCut Caption Extractor tool."""
    
    def __init__(self, master=None, on_back: Callable = None):
        super().__init__(master)
        
        self.on_back = on_back
        self.captions: List[CaptionItem] = []
        self.current_file: Optional[str] = None
        
        # Configure window
        self.title("📝 CapCut Caption Extractor")
        self.geometry("650x600")
        self.minsize(600, 550)
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Build UI
        self._create_widgets()
        
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
        # Main container
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # === Header ===
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 15))
        
        # Back button
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
            text="📝 CapCut Caption Extractor",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(side="left")
        
        # === File Selection ===
        self.file_frame = ctk.CTkFrame(self.main_frame)
        self.file_frame.pack(fill="x", pady=(0, 15))
        
        self.file_title = ctk.CTkLabel(
            self.file_frame,
            text="📂 Chọn file draft_content.json hoặc folder project CapCut:",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        self.file_title.pack(fill="x", padx=12, pady=(10, 5))
        
        self.file_inner_frame = ctk.CTkFrame(self.file_frame, fg_color="transparent")
        self.file_inner_frame.pack(fill="x", padx=12, pady=(0, 10))
        
        self.file_path_label = ctk.CTkLabel(
            self.file_inner_frame,
            text="Chưa chọn file...",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="w",
            wraplength=400
        )
        self.file_path_label.pack(side="left", fill="x", expand=True)
        
        self.browse_folder_btn = ctk.CTkButton(
            self.file_inner_frame,
            text="📁 Folder",
            font=ctk.CTkFont(size=11),
            width=70,
            height=28,
            corner_radius=6,
            command=self._on_browse_folder,
            fg_color="#9b59b6",
            hover_color="#8e44ad"
        )
        self.browse_folder_btn.pack(side="right", padx=(5, 0))
        
        self.browse_file_btn = ctk.CTkButton(
            self.file_inner_frame,
            text="📄 File",
            font=ctk.CTkFont(size=11),
            width=60,
            height=28,
            corner_radius=6,
            command=self._on_browse_file,
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        self.browse_file_btn.pack(side="right")
        
        # === Preview ===
        self.preview_label = ctk.CTkLabel(
            self.main_frame,
            text="📋 Preview Caption:",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        self.preview_label.pack(fill="x", pady=(5, 5))
        
        self.preview_text = ctk.CTkTextbox(
            self.main_frame,
            font=ctk.CTkFont(size=12),
            corner_radius=10,
            wrap="word"
        )
        self.preview_text.pack(fill="both", expand=True, pady=(0, 15))
        self.preview_text.insert("1.0", "💡 Chọn file draft_content.json từ project CapCut để xem caption.\n\n"
                                        "Vị trí thường gặp:\n"
                                        "C:\\Users\\<user>\\AppData\\Local\\CapCut\\User Data\\Projects\\com.lveditor.draft\\<project_id>\\")
        self.preview_text.configure(state="disabled")
        
        # === Export Options ===
        self.export_frame = ctk.CTkFrame(self.main_frame)
        self.export_frame.pack(fill="x", pady=(0, 10))
        
        self.format_label = ctk.CTkLabel(
            self.export_frame,
            text="📥 Định dạng xuất:",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        self.format_label.pack(side="left", padx=12, pady=10)
        
        self.format_var = ctk.StringVar(value="srt")
        self.format_selector = ctk.CTkSegmentedButton(
            self.export_frame,
            values=["srt", "txt", "txt_timing"],
            variable=self.format_var,
            font=ctk.CTkFont(size=11)
        )
        self.format_selector.pack(side="left", padx=10, pady=10)
        
        self.export_btn = ctk.CTkButton(
            self.export_frame,
            text="💾 Xuất File",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=100,
            height=32,
            corner_radius=6,
            command=self._on_export,
            fg_color="#27ae60",
            hover_color="#1e8449",
            state="disabled"
        )
        self.export_btn.pack(side="right", padx=12, pady=10)
        
        # === Status Bar ===
        self.status_frame = ctk.CTkFrame(self.main_frame, height=30)
        self.status_frame.pack(fill="x")
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Sẵn sàng",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        self.count_label = ctk.CTkLabel(
            self.status_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.count_label.pack(side="right", padx=10, pady=5)
    
    def _on_browse_file(self):
        """Browse for draft_content.json file."""
        file_path = filedialog.askopenfilename(
            title="Chọn file draft_content.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self._load_file(file_path)
    
    def _on_browse_folder(self):
        """Browse for CapCut project folder."""
        folder_path = filedialog.askdirectory(
            title="Chọn folder project CapCut"
        )
        
        if folder_path:
            # Find draft_content.json in folder
            draft_file = CapCutParser.find_draft_file(folder_path)
            if draft_file:
                self._load_file(draft_file)
            else:
                messagebox.showwarning(
                    "Không tìm thấy",
                    "Không tìm thấy file draft_content.json trong folder này."
                )
    
    def _load_file(self, file_path: str):
        """Load and parse a draft file."""
        self.current_file = file_path
        self.file_path_label.configure(text=file_path, text_color="#3498db")
        self.status_label.configure(text="🔄 Đang phân tích...")
        self.update()
        
        try:
            self.captions = CapCutParser.parse_draft(file_path)
            
            if self.captions:
                # Show preview
                preview_text = CapCutParser.to_txt(self.captions)
                self.preview_text.configure(state="normal")
                self.preview_text.delete("1.0", "end")
                self.preview_text.insert("1.0", preview_text)
                self.preview_text.configure(state="disabled")
                
                # Update status
                self.status_label.configure(text="✅ Đã tải thành công")
                self.count_label.configure(text=f"📝 {len(self.captions)} caption")
                self.export_btn.configure(state="normal")
            else:
                self.preview_text.configure(state="normal")
                self.preview_text.delete("1.0", "end")
                self.preview_text.insert("1.0", "⚠️ Không tìm thấy caption trong file này.\n\n"
                                                "Hãy đảm bảo project có caption/text đã được tạo.")
                self.preview_text.configure(state="disabled")
                self.status_label.configure(text="⚠️ Không có caption")
                self.count_label.configure(text="")
                self.export_btn.configure(state="disabled")
                
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))
            self.status_label.configure(text="❌ Lỗi đọc file")
            self.export_btn.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")
            self.status_label.configure(text="❌ Lỗi")
            self.export_btn.configure(state="disabled")
    
    def _on_export(self):
        """Export captions to file."""
        if not self.captions:
            messagebox.showwarning("Cảnh báo", "Không có caption để xuất!")
            return
        
        format_type = self.format_var.get()
        
        # Determine file extension and content
        if format_type == "srt":
            extension = ".srt"
            content = CapCutParser.to_srt(self.captions)
            file_types = [("SRT files", "*.srt")]
        elif format_type == "txt":
            extension = ".txt"
            content = CapCutParser.to_txt(self.captions)
            file_types = [("Text files", "*.txt")]
        else:  # txt_timing
            extension = ".txt"
            content = CapCutParser.to_txt_with_timing(self.captions)
            file_types = [("Text files", "*.txt")]
        
        # Get default filename from source
        default_name = "captions"
        if self.current_file:
            folder = os.path.dirname(self.current_file)
            # Try to find project name from folder structure
            parent_folder = os.path.basename(os.path.dirname(folder))
            if parent_folder:
                default_name = parent_folder
        
        # Ask for save location
        save_path = filedialog.asksaveasfilename(
            title="Lưu file caption",
            defaultextension=extension,
            initialfile=default_name + extension,
            filetypes=file_types
        )
        
        if save_path:
            try:
                # Use UTF-8 with BOM for SRT files (CapCut compatibility)
                encoding = 'utf-8-sig' if format_type == "srt" else 'utf-8'
                with open(save_path, 'w', encoding=encoding, newline='') as f:
                    f.write(content)
                
                self.status_label.configure(text=f"✅ Đã lưu: {os.path.basename(save_path)}")
                messagebox.showinfo("Thành công", f"Đã xuất caption thành công!\n\n{save_path}")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")
                self.status_label.configure(text="❌ Lỗi lưu file")
