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
- **Subtitle Download**: Download subtitles in multiple languages and formats
- **Image Download**: Download cover and poster images with configurable settings
- **Genre Filtering**: Skip unwanted genres from metadata

## Installation

### Method 1: Global Installation (Recommended)

#### Option A: Using install script (Recommended)
```bash
# Clone the repository
git clone https://github.com/ZephyrX11/JAV-NFO-Generator
cd JAV-NFO-Generator

# Run the installation script
./install.sh  # Linux/Mac
# OR
install.bat   # Windows
```

#### Option B: Using pipx (Recommended for Arch Linux)
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

#### Option C: Using pip directly
```bash
# Clone the repository
git clone https://github.com/ZephyrX11/JAV-NFO-Generator
cd JAV-NFO-Generator

# Install globally
python -m pip install --user -e .
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

# Download subtitles
jav-nfo search --id XXX-123 --subtitles

# Generate NFO file with translation and subtitles
jav-nfo search --id XXX-123 --nfo --translate --subtitles

# Download images
jav-nfo search --id XXX-123 --images

# Generate NFO file with translation, subtitles, and images
jav-nfo search --id XXX-123 --nfo --translate --subtitles --images
```

### Auto Detection
```bash
# Basic auto detection
jav-nfo auto

# Auto detection with translation
jav-nfo auto --translate

# Auto detection with subtitles
jav-nfo auto --subtitles

# Auto detection with translation and subtitles
jav-nfo auto --translate --subtitles

# Auto detection with images
jav-nfo auto --images

# Auto detection with depth limit (search 2 levels deep)
jav-nfo auto --depth 2

# Auto detection with translation, subtitles, and images
jav-nfo auto --translate --subtitles --images

# Auto detection with depth limit and all features
jav-nfo auto --depth 3 --translate --subtitles --images
```

### Depth Control
The `--depth` flag controls how many subdirectory levels to search:
- `--depth 0` (default): Search current directory only
- `--depth 1`: Search current directory + 1 level deep
- `--depth 2`: Search current directory + 2 levels deep
- And so on...

**Examples:**
```
Directory structure:
/videos/
├── 2024/
│   ├── SONE-682.mp4
│   └── ABC-123.mp4
└── 2025/
    └── DEF-456.mp4

Commands:
jav-nfo auto --depth 0  # Only finds files in /videos/
jav-nfo auto --depth 1  # Finds files in /videos/, /videos/2024/, /videos/2025/
jav-nfo auto --depth 2  # Finds all files in the entire structure
```

### Batch Processing
```bash
# Basic batch processing
jav-nfo batch --directory /path/to/videos

# Batch processing with translation
jav-nfo batch --directory /path/to/videos --translate

# Batch processing with subtitles
jav-nfo batch --directory /path/to/videos --subtitles

# Batch processing with translation and subtitles
jav-nfo batch --directory /path/to/videos --translate --subtitles

# Batch processing with images
jav-nfo batch --directory /path/to/videos --images

# Batch processing with depth limit (search 1 level deep)
jav-nfo batch --directory /path/to/videos --depth 1

# Batch processing with translation, subtitles, and images
jav-nfo batch --directory /path/to/videos --translate --subtitles --images

# Batch processing with depth limit and all features
jav-nfo batch --directory /path/to/videos --depth 2 --translate --subtitles --images
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

## Image Download

The tool supports downloading cover and poster images for JAV content with configurable settings:

### **Features:**
- **Cover Images**: Download high-quality cover images (fanart.jpg)
- **Poster Images**: Download poster images (folder.jpg)
- **Configurable Naming**: Customizable filename prefixes
- **Timeout Control**: Configurable download timeout
- **Selective Download**: Enable/disable cover and poster separately
- **CLI Override**: Force download with `--images` flag

### **Configuration Options:**
- **IMAGE_DOWNLOAD_ENABLED**: Enable/disable image downloading
- **IMAGE_DOWNLOAD_COVER**: Enable/disable cover image download
- **IMAGE_DOWNLOAD_POSTER**: Enable/disable poster image download
- **IMAGE_FILENAME_COVER**: Cover image filename prefix (default: "fanart")
- **IMAGE_FILENAME_POSTER**: Poster image filename prefix (default: "folder")
- **IMAGE_DOWNLOAD_TIMEOUT**: Download timeout in seconds (default: 15)

### **CLI Flag Behavior:**
- **`--images` flag**: Always enables image download, even if `IMAGE_DOWNLOAD_ENABLED=false` in settings
- **Settings priority**: CLI flags override configuration settings
- **Force download**: Use `--images` to force download regardless of settings

### **Usage:**
```bash
# Enable image download in .env file
IMAGE_DOWNLOAD_ENABLED=true
IMAGE_DOWNLOAD_COVER=true
IMAGE_DOWNLOAD_POSTER=true

# Download images with metadata
jav-nfo search --id XXX-123 --nfo

# Download images using CLI flag (overrides settings)
jav-nfo search --id XXX-123 --images

# Download images with translation
jav-nfo search --id XXX-123 --images --translate
```

## Subtitle Download

The tool supports downloading subtitles for JAV content with configurable languages and formats:

### **Features:**
- **Multiple Languages**: Download subtitles in English, Japanese, and other languages
- **Multiple Formats**: Support for SRT, ASS, VTT, and other subtitle formats
- **Flexible Naming**: Customizable filename templates with placeholders
- **Organized Output**: Save subtitles to custom directories or alongside video files
- **Batch Processing**: Download subtitles for multiple files at once

### **Configuration Options:**
- **SUBTITLE_DOWNLOAD_ENABLED**: Enable/disable subtitle downloading (can be overridden by CLI flag)
- **SUBTITLE_LANGUAGES**: Comma-separated list of preferred languages (e.g., "en,ja")
- **SUBTITLE_FORMAT**: Subtitle format (srt, ass, vtt, etc.)
- **SUBTITLE_OUTPUT_DIR**: Custom output directory (empty for same directory as video)
- **SUBTITLE_FILENAME_TEMPLATE**: Filename template with placeholders (fallback only):
  - `<ID>`: JAV ID
  - `<LANG>`: Language code
  - `<EXT>`: File extension

### **CLI Flag Behavior:**
- **`--subtitles` flag**: Always enables subtitle download, even if `SUBTITLE_DOWNLOAD_ENABLED=false` in settings
- **Settings priority**: CLI flags override configuration settings
- **Force download**: Use `--subtitles` to force download regardless of settings

### **Subtitle Naming:**
Subtitles are automatically named based on the video filename to prevent overwriting:
- **Format**: `{video_name}.{language}.{format}` or `{video_name}.{language}.{counter}.{format}`
- **Example**: `SONE-682.en.srt`, `SONE-682.ja.srt`, `SONE-682.en.1.srt`
- **Location**: Same directory as the video file
- **Multiple Sources**: If multiple subtitle sources exist, they get numbered (1, 2, 3...)
- **No Overwriting**: Each subtitle file gets a unique name

### **Usage:**
```bash
# Enable subtitle download in .env file
SUBTITLE_DOWNLOAD_ENABLED=true
SUBTITLE_LANGUAGES=en,ja
SUBTITLE_FORMAT=srt

# Download subtitles with metadata
jav-nfo search --id XXX-123 --nfo

# Download subtitles using CLI flag (overrides settings)
jav-nfo search --id XXX-123 --subtitles

# Download subtitles with translation
jav-nfo search --id XXX-123 --subtitles --translate

# Force subtitle download even if disabled in settings
jav-nfo search --id XXX-123 --subtitles
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

# Subtitle download settings
SUBTITLE_DOWNLOAD_ENABLED=false
SUBTITLE_LANGUAGES=en,ja
SUBTITLE_FORMAT=srt
SUBTITLE_OUTPUT_DIR=
SUBTITLE_FILENAME_TEMPLATE=<ID>.<LANG>.<EXT>

# Image download settings
IMAGE_DOWNLOAD_ENABLED=true
IMAGE_DOWNLOAD_COVER=true
IMAGE_DOWNLOAD_POSTER=true
IMAGE_FILENAME_COVER=fanart
IMAGE_FILENAME_POSTER=folder
IMAGE_DOWNLOAD_TIMEOUT=15

# Genres to skip (comma-separated)
SKIP_GENRES=4K,ハイビジョン,独占配信

# Cache settings
CACHE_ENABLED=true
CACHE_FILE=
```

## License

MIT License 
