@echo off
echo ====================================
echo YouTube Downloader - Build Script
echo ====================================
echo.

REM Create virtual environment if not exists
if not exist "venv" (
    echo Creating virtual environment...
    py -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
py -m pip install -r requirements.txt

REM Build executable
echo Building executable...
py -m PyInstaller build.spec --clean

echo.
echo ====================================
echo Build complete!
echo Executable: dist\YouTubeDownloader.exe
echo ====================================

pause
