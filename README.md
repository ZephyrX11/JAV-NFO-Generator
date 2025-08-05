# JAV NFO Generator

A Python CLI tool for scraping JAV metadata from various sites and generating .nfo files for media management.

## Features

- **Manual Search**: Search for metadata using a specific JAV code
- **Auto Detection**: Automatically scan current directory for .mp4 files and extract JAV codes from filenames
- **Multiple Sources**: Support for multiple metadata sources (Fanza, etc.)
- **NFO Generation**: Generate properly formatted .nfo files for media management
- **Batch Processing**: Process multiple files at once
- **Translation Support**: Translate metadata to English with Google Translate or DeepL
- **Translation Cache**: Cache translated values to ensure consistency and reduce API calls
- **Genre Filtering**: Skip unwanted genres from metadata

## Installation

### Method 1: Global Installation (Recommended)

#### Option A: Using pipx (Recommended for Arch Linux)
```bash
# Install pipx if not already installed
sudo pacman -S python-pipx  # Arch Linux
# OR
python -m pip install --user pipx  # Other systems

# Clone the repository
git clone https://github.com/ZephyrX11/JAV-NFO-Generator
cd JAV-NFO-Generator

# Install globally using pipx
pipx install -e .
```

#### Option B: Using pip (Other systems)
```bash
# Clone the repository
git clone https://github.com/ZephyrX11/JAV-NFO-Generator
cd JAV-NFO-Generator

# Install globally
python -m pip install --user -e .
```

#### Option C: Manual PATH setup
```bash
# Clone the repository
git clone https://github.com/ZephyrX11/JAV-NFO-Generator
cd JAV-NFO-Generator

# Install dependencies
pip install -r requirements.txt

# Make the script executable
chmod +x jav-nfo

# Add to PATH (add this to your ~/.bashrc or ~/.zshrc)
export PATH="$PATH:$(pwd)"

# Or copy to a directory in your PATH
sudo cp jav-nfo /usr/local/bin/
```

### Method 2: Local Development

1. Clone the repository:
```bash
git clone https://github.com/ZephyrX11/JAV-NFO-Generator
cd JAV-NFO-Generator
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the tool:
```bash
python main.py --help
```

## Usage

After installation, you can use the tool globally with these commands:

### Manual Search
```bash
# Output metadata to terminal (default)
jav-nfo search --id XXX-123
# or locally: python main.py search --id XXX-123

# Generate NFO file
jav-nfo search --id XXX-123 --nfo

# Translate metadata to English
jav-nfo search --id XXX-123 --translate

# Generate NFO file with translation
jav-nfo search --id XXX-123 --nfo --translate
```

### Auto Detection
```bash
# Basic auto detection
jav-nfo auto

# Auto detection with translation
jav-nfo auto --translate
```

### Batch Processing
```bash
# Basic batch processing
jav-nfo batch --directory /path/to/videos

# Batch processing with translation
jav-nfo batch --directory /path/to/videos --translate
```

### Other Commands
```bash
# List available scrapers
jav-nfo list-scrapers

# Test a specific scraper
jav-nfo test --scraper fanza --id XXX-123

# Cache management
jav-nfo cache-stats                    # Show cache statistics
jav-nfo clear-cache                    # Clear all cache
jav-nfo clear-cache --field genres     # Clear specific field cache
jav-nfo export-cache --output cache.json  # Export cache to file
jav-nfo import-cache --input cache.json   # Import cache from file

# Show help
jav-nfo --help
```

## File Structure

```
python_jav_nfo_generator/
├── main.py                 # Main CLI entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── config/
│   └── settings.py        # Configuration settings
├── scrapers/
│   ├── __init__.py
│   ├── base.py           # Base scraper class
│   ├── fanza.py          # Fanza scraper implementation
│   └── factory.py        # Scraper factory
├── generators/
│   ├── __init__.py
│   └── nfo.py            # NFO file generator
├── utils/
│   ├── __init__.py
│   ├── file_utils.py     # File handling utilities
│   └── pattern.py        # Pattern matching utilities
└── tests/
    └── __init__.py
```

## Translation Cache

The tool includes a smart translation cache system that stores translated values to ensure consistency and reduce API calls:

### **Benefits:**
- **Consistency**: Same Japanese terms always translate to the same English equivalents
- **Performance**: Cached translations are instant, no API calls needed
- **Cost Savings**: Reduces translation API usage
- **Reliability**: Works offline for previously translated content
- **Smart Caching**: Individual genres and actresses are cached separately for maximum reuse

### **Cache Storage:**
- **Location**: `~/.jav_nfo_generator/translation_cache.json`
- **Fields Cached**: genres, actress, director, studio, label, series
- **Smart Caching**: Comma-separated values (genres, actress) are cached individually
- **Automatic**: Cache is updated automatically during translation

### **Cache Management:**
```bash
# View cache statistics
jav-nfo cache-stats

# Clear all cache
jav-nfo clear-cache

# Clear specific field cache
jav-nfo clear-cache --field genres

# Export cache for backup/sharing
jav-nfo export-cache --output cache_backup.json

# Import cache from file
jav-nfo import-cache --input cache_backup.json
```

## Configuration

Create a `.env` file in the project root to configure settings:

```env
# User agent for requests
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

# Request delays (in seconds)
REQUEST_DELAY=1.0

# Output settings
DEFAULT_OUTPUT_DIR=./nfo_files

# Translation settings
TRANSLATION_ENABLED=false
TRANSLATION_API_KEY=
TRANSLATION_SERVICE=google
TRANSLATION_TARGET_LANG=en
TRANSLATION_SOURCE_LANG=ja
TRANSLATION_FIELDS=title,plot,genres,actress,director,studio,label,series

# Genres to skip (comma-separated)
SKIP_GENRES=4K,ハイビジョン,独占配信

# Cache settings
CACHE_ENABLED=true
CACHE_FILE=
```

## License

MIT License 
