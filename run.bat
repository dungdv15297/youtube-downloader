@echo off
echo Starting YouTube Downloader...

REM Check if venv exists
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe src\main.py
) else (
    REM Try system Python with py launcher
    py src\main.py
)
