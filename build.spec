# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller build specification for YouTube Downloader.
Run with: pyinstaller build.spec
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all yt-dlp data
yt_dlp_datas = collect_data_files('yt_dlp')
yt_dlp_hiddenimports = collect_submodules('yt_dlp')

# Collect customtkinter data
ctk_datas = collect_data_files('customtkinter')

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=yt_dlp_datas + ctk_datas,
    hiddenimports=yt_dlp_hiddenimports + [
        'customtkinter',
        'PIL',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YouTubeDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)
