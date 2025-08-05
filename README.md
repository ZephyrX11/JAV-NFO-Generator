# JAV NFO Generator

A Python CLI tool for scraping JAV metadata from various sites and generating .nfo files for media management.

## Features

- **Manual Search**: Search for metadata using a specific JAV code
- **Auto Detection**: Automatically scan current directory for .mp4 files and extract JAV codes from filenames
- **Multiple Sources**: Support for multiple metadata sources (Fanza, etc.)
- **NFO Generation**: Generate properly formatted .nfo files for media management
- **Batch Processing**: Process multiple files at once

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd python_jav_nfo_generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Manual Search
```bash
# Output metadata to terminal (default)
python main.py search --id XXX-123

# Generate NFO file
python main.py search --id XXX-123 --nfo

# Translate metadata to English (overrides settings)
python main.py search --id XXX-123 --translate

# Generate NFO file with translation (overrides settings)
python main.py search --id XXX-123 --nfo --translate
```

### Auto Detection
```bash
# Basic auto detection
python main.py auto

# Auto detection with translation (overrides settings)
python main.py auto --translate
```

### Batch Processing
```bash
# Basic batch processing
python main.py batch --directory /path/to/videos

# Batch processing with translation (overrides settings)
python main.py batch --directory /path/to/videos --translate
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

## Configuration

Create a `.env` file in the project root to configure settings:

```env
# API endpoints
FANZA_API_URL=https://api.video.dmm.co.jp/graphql

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
```

## License

MIT License 