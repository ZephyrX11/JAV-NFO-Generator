#!/bin/bash

# JAV NFO Generator Installation Script

echo "🚀 Installing JAV NFO Generator globally..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $python_version is installed, but Python $required_version or higher is required."
    exit 1
fi

echo "✅ Python $python_version detected"

# Check if we're on Arch Linux
if command -v pacman &> /dev/null; then
    echo "🐧 Arch Linux detected"
    
    # Check if pipx is installed
    if ! command -v pipx &> /dev/null; then
        echo "📦 Installing pipx..."
        sudo pacman -S python-pipx --noconfirm
    fi
    
    # Install the package using pipx
    echo "📦 Installing package using pipx..."
    pipx install -e .
else
    # Install the package using pip
    echo "📦 Installing package using pip..."
    python3 -m pip install --user -e .
fi

if [ $? -eq 0 ]; then
    echo "✅ Installation successful!"
    echo ""
    echo "🎉 You can now use the tool globally with these commands:"
    echo "   jav-nfo --help"
    echo "   javnfo --help"
    echo ""
    echo "📖 Examples:"
    echo "   jav-nfo search --id sone00638"
    echo "   jav-nfo search --id SONE-638 --translate"
    echo "   jav-nfo auto --translate"
    echo ""
    echo "🔧 To uninstall, run: python3 -m pip uninstall jav-nfo-generator"
else
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi 