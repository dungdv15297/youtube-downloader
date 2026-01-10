# YouTube Downloader

🎬 Ứng dụng Windows đơn giản để tải video YouTube.

## Tính năng

- ✅ Paste link YouTube bằng một click
- ✅ Tự động xác nhận URL YouTube hợp lệ
- ✅ Hiển thị thông tin video trước khi tải
- ✅ Thanh tiến độ tải xuống
- ✅ Chọn thư mục lưu video
- ✅ Giao diện dark mode hiện đại

## Cài đặt & Chạy

### Cách 1: Chạy từ source code

```bash
# Cài đặt dependencies
py -m pip install -r requirements.txt

# Chạy ứng dụng
py src/main.py
```

Hoặc dùng file `run.bat`:
```bash
run.bat
```

### Cách 2: Build executable

```bash
# Setup và build
build.bat
```

Executable sẽ được tạo tại `dist/YouTubeDownloader.exe`

### Cách 3: Tạo installer

1. Cài đặt [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Build executable trước (bước trên)
3. Mở `installer.iss` bằng Inno Setup
4. Compile để tạo file installer

## Cách sử dụng

1. Mở ứng dụng
2. Copy một link YouTube (Ctrl+C)
3. Click nút **PASTE LINK**
4. Xem thông tin video
5. Click **TẢI XUỐNG**
6. Video sẽ được lưu vào thư mục đã chọn

## Cấu trúc dự án

```
Youtube Downloader/
├── src/
│   ├── main.py           # Entry point
│   ├── validator.py      # YouTube URL validation
│   ├── downloader.py     # yt-dlp download wrapper
│   ├── settings.py       # Settings management
│   └── ui/
│       └── main_window.py # GUI implementation
├── requirements.txt      # Python dependencies
├── build.spec           # PyInstaller config
├── installer.iss        # Inno Setup script
├── build.bat            # Build script
└── run.bat              # Run script
```

## Yêu cầu hệ thống

- Windows 10/11
- Python 3.8+ (nếu chạy từ source)
- Kết nối Internet

## License

MIT License
