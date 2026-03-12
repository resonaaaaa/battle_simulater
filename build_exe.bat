@echo off
setlocal

cd /d %~dp0

set "PYTHON_EXE="
if exist "%cd%\.venv\Scripts\python.exe" set "PYTHON_EXE=%cd%\.venv\Scripts\python.exe"
if not defined PYTHON_EXE if exist "%cd%\.venv\bin\python.exe" set "PYTHON_EXE=%cd%\.venv\bin\python.exe"
if not defined PYTHON_EXE set "PYTHON_EXE=python"

echo Using Python: %PYTHON_EXE%

%PYTHON_EXE% -m pip --version >nul 2>&1
if errorlevel 1 (
    echo pip not found, bootstrapping with ensurepip...
    %PYTHON_EXE% -m ensurepip --upgrade
)

%PYTHON_EXE% -m pip --version >nul 2>&1
if errorlevel 1 (
    echo Failed to initialize pip in selected Python environment.
    exit /b 1
)

echo [1/3] Installing/Updating PyInstaller...
%PYTHON_EXE% -m pip install --upgrade pyinstaller
if errorlevel 1 (
    echo Failed to install PyInstaller.
    exit /b 1
)

echo [2/3] Building EXE...
%PYTHON_EXE% -m PyInstaller --noconfirm --clean --onefile --windowed --name battle_simulator battle_gui.py
if errorlevel 1 (
    echo Build failed.
    exit /b 1
)

echo [3/3] Copying EXE to project root...
if exist dist\battle_simulator.exe (
    copy /Y dist\battle_simulator.exe . >nul
    echo Done: %cd%\battle_simulator.exe
) else (
    echo EXE not found under dist folder.
    exit /b 1
)

echo.
echo Build complete. You can distribute battle_simulator.exe directly.
endlocal
