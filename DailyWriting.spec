# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for DailyWriting.app

Usage:
    pyinstaller DailyWriting.spec

This creates a standalone macOS application in the dist/ directory.
"""

import sys
from pathlib import Path

# App metadata
APP_NAME = "DailyWriting"
APP_VERSION = "1.0.0"
APP_BUNDLE_ID = "com.dailywriting.app"

# Paths
project_root = Path(SPECPATH)
icon_path = project_root / "resources" / "icon.icns"

# Analysis
a = Analysis(
    ["main.py"],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        ("data", "data"),
        ("core", "core"),
        ("ui", "ui"),
    ],
    hiddenimports=[
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "google.genai",
        "google.genai.types",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "numpy",
        "scipy",
        "pandas",
        "PIL",
        "cv2",
        "tensorflow",
        "torch",
        "pytest",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)

app = BUNDLE(
    coll,
    name=f"{APP_NAME}.app",
    icon=str(icon_path) if icon_path.exists() else None,
    bundle_identifier=APP_BUNDLE_ID,
    version=APP_VERSION,
    info_plist={
        "CFBundleName": APP_NAME,
        "CFBundleDisplayName": APP_NAME,
        "CFBundleIdentifier": APP_BUNDLE_ID,
        "CFBundleVersion": APP_VERSION,
        "CFBundleShortVersionString": APP_VERSION,
        "NSHighResolutionCapable": True,
        "NSRequiresAquaSystemAppearance": False,
        "LSMinimumSystemVersion": "10.15",
        "NSHumanReadableCopyright": "Copyright © 2025",
    },
)
