@echo off
echo ====================================
echo Installing FFmpeg for YouTube Downloader
echo ====================================
echo.

REM Check if winget is available
winget --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: winget is not available. Please install FFmpeg manually.
    echo Download from: https://ffmpeg.org/download.html
    pause
    exit /b 1
)

echo Installing FFmpeg via winget...
winget install -e --id Gyan.FFmpeg

echo.
echo ====================================
echo FFmpeg installed successfully!
echo Please restart the app to use high quality downloads.
echo ====================================
pause
