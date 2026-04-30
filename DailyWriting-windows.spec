# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for DailyWriting on Windows.

Usage:
    pyinstaller DailyWriting-windows.spec

Output:
    dist\\DailyWriting\\DailyWriting.exe (with bundled dependencies in dist\\DailyWriting\\)
"""

from pathlib import Path

APP_NAME = "DailyWriting"
APP_VERSION = "1.3.0"

project_root = Path(SPECPATH)
icon_path = project_root / "resources" / "icon.ico"

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
        "anthropic",
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_path) if icon_path.exists() else None,
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
