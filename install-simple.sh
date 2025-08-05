#!/bin/bash

# Simple JAV NFO Generator Installation Script

echo "🚀 Installing JAV NFO Generator..."

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

# Install dependencies
echo "📦 Installing dependencies..."
python3 -m pip install --user -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies."
    exit 1
fi

# Make the script executable
echo "🔧 Making script executable..."
chmod +x jav-nfo

# Get the current directory
current_dir=$(pwd)

echo "✅ Installation successful!"
echo ""
echo "🎉 You can now use the tool in these ways:"
echo ""
echo "1. From the current directory:"
echo "   ./jav-nfo --help"
echo ""
echo "2. Add to PATH (add this line to your ~/.bashrc or ~/.zshrc):"
echo "   export PATH=\"\$PATH:$current_dir\""
echo "   Then run: jav-nfo --help"
echo ""
echo "3. Copy to system PATH:"
echo "   sudo cp jav-nfo /usr/local/bin/"
echo "   Then run: jav-nfo --help"
echo ""
echo "📖 Examples:"
echo "   jav-nfo search --id sone00638"
echo "   jav-nfo search --id SONE-638 --translate"
echo "   jav-nfo auto --translate" 