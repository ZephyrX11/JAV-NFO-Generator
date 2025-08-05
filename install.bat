@echo off
REM JAV NFO Generator Installation Script for Windows

echo 🚀 Installing JAV NFO Generator globally...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo ✅ Python %python_version% detected

REM Install the package
echo 📦 Installing package...
python -m pip install --user -e .

if errorlevel 1 (
    echo ❌ Installation failed. Please check the error messages above.
    pause
    exit /b 1
) else (
    echo ✅ Installation successful!
    echo.
    echo 🎉 You can now use the tool globally with these commands:
    echo    jav-nfo --help
    echo    javnfo --help
    echo.
    echo 📖 Examples:
    echo    jav-nfo search --id sone00638
    echo    jav-nfo search --id SONE-638 --translate
    echo    jav-nfo auto --translate
    echo.
    echo 🔧 To uninstall, run: python -m pip uninstall jav-nfo-generator
    pause
) 