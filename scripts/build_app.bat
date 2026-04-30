@echo off
REM Build DailyWriting.exe for Windows
REM
REM Usage: scripts\build_app.bat
REM
REM Prerequisites:
REM   - Python 3.9+
REM   - PyInstaller and Pillow (auto-installed if missing)
REM
REM Output:
REM   - dist\DailyWriting\DailyWriting.exe (with bundled dependencies)

setlocal enabledelayedexpansion

REM Move to project root (parent of this script's dir)
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%.."

echo === Building DailyWriting.exe ===
echo Project root: %CD%

REM Activate venv if present
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: No venv found. Using system Python.
)

REM Ensure PyInstaller is available
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller || goto :build_failed
)

REM Ensure Pillow is available (used by create_icon.py)
python -c "import PIL" 2>nul
if errorlevel 1 (
    echo Installing Pillow for icon generation...
    pip install Pillow || goto :build_failed
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Generate Windows icon if missing
if not exist "resources\icon.ico" (
    echo Creating icon...
    python scripts\create_icon.py || goto :build_failed
)

REM Run PyInstaller
echo Building application with PyInstaller...
pyinstaller DailyWriting-windows.spec --noconfirm
if errorlevel 1 goto :build_failed

REM Verify build
if exist "dist\DailyWriting\DailyWriting.exe" (
    echo.
    echo === Build Successful! ===
    echo.
    echo Application: dist\DailyWriting\DailyWriting.exe
    echo To run: dist\DailyWriting\DailyWriting.exe
    echo.
    goto :end
)

:build_failed
echo.
echo Build failed. Check output above for errors.
exit /b 1

:end
endlocal
