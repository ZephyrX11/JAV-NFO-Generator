import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings and configuration."""
    
    # API Settings
    FANZA_API_URL = os.getenv("FANZA_API_URL", "https://api.video.dmm.co.jp/graphql")
    
    # Request Settings
    USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "1.0"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # Output Settings
    DEFAULT_OUTPUT_DIR = os.getenv("DEFAULT_OUTPUT_DIR", "")
    
    # Output directory template with tags (user can set this)
    # Available tags: <YEAR>, <ID>, <STUDIO>, <TITLE> 
    OUTPUT_DIR_TEMPLATE = os.getenv("OUTPUT_DIR_TEMPLATE", "<YEAR>/<ID>")

    # Video file name template
    OUTPUT_VIDEO_NAME_TEMPLATE = os.getenv("OUTPUT_VIDEO_NAME_TEMPLATE", "<ID><EXT>")
    
    # Translation Settings
    TRANSLATION_ENABLED = os.getenv("TRANSLATION_ENABLED", "false").lower() == "true"
    TRANSLATION_API_KEY = os.getenv("TRANSLATION_API_KEY", "")
    TRANSLATION_SERVICE = os.getenv("TRANSLATION_SERVICE", "google")  # google, deepl, etc.
    TRANSLATION_TARGET_LANG = os.getenv("TRANSLATION_TARGET_LANG", "en")
    TRANSLATION_SOURCE_LANG = os.getenv("TRANSLATION_SOURCE_LANG", "ja")
    
    # Fields to translate (comma-separated)
    TRANSLATION_FIELDS = os.getenv("TRANSLATION_FIELDS", "title,plot,genres,actresses,directors,studio,label,series").split(",")
    
    # Subtitle Download Settings
    SUBTITLE_DOWNLOAD_ENABLED = os.getenv("SUBTITLE_DOWNLOAD_ENABLED", "true").lower() == "true"
    SUBTITLE_LANGUAGES = os.getenv("SUBTITLE_LANGUAGES", "en").split(",")  # Preferred languages in order
    SUBTITLE_FORMAT = os.getenv("SUBTITLE_FORMAT", "srt")  # srt, ass, vtt, etc.
    SUBTITLE_OUTPUT_DIR = os.getenv("SUBTITLE_OUTPUT_DIR", "")  # Empty for same directory as video
    SUBTITLE_FILENAME_TEMPLATE = os.getenv("SUBTITLE_FILENAME_TEMPLATE", "<ID>.<LANG>.<EXT>")
    
    # Image Download Settings
    IMAGE_DOWNLOAD_ENABLED = os.getenv("IMAGE_DOWNLOAD_ENABLED", "true").lower() == "true"
    IMAGE_DOWNLOAD_COVER = os.getenv("IMAGE_DOWNLOAD_COVER", "true").lower() == "true"
    IMAGE_DOWNLOAD_POSTER = os.getenv("IMAGE_DOWNLOAD_POSTER", "true").lower() == "true"
    IMAGE_FILENAME_COVER = os.getenv("IMAGE_FILENAME_COVER", "fanart")  # fanart.jpg
    IMAGE_FILENAME_POSTER = os.getenv("IMAGE_FILENAME_POSTER", "folder")  # folder.jpg
    IMAGE_DOWNLOAD_TIMEOUT = int(os.getenv("IMAGE_DOWNLOAD_TIMEOUT", "15"))
    
    # Genres to skip (comma-separated)
    SKIP_GENRES = os.getenv("SKIP_GENRES", "4K,ハイビジョン,独占配信").split(",")
    
    # Cache settings
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_FILE = os.getenv("CACHE_FILE", "")  # Empty for default location
    
    # Multi-Scraper Settings
    ENABLED_SCRAPERS = ['fanza', 'r18dev']

    # R18.dev Language Settings
    R18DEV_LANGUAGE = os.getenv("R18DEV_LANGUAGE", "en")  # "en" | "jp"
    
    # Field Priority Settings - which scraper to prefer for each field
    # Format: list of scrapers in order of preference
    FIELD_PRIORITY_TITLE = ['r18dev', 'fanza']
    FIELD_PRIORITY_ACTRESSES = ['r18dev', 'fanza']
    FIELD_PRIORITY_DIRECTORS = ['r18dev', 'fanza']
    FIELD_PRIORITY_CATEGORIES = ['r18dev', 'fanza']
    FIELD_PRIORITY_STUDIO = ['r18dev', 'fanza']
    FIELD_PRIORITY_SERIES = ['r18dev', 'fanza']
    FIELD_PRIORITY_RELEASE_DATE = ['r18dev', 'fanza']
    FIELD_PRIORITY_RUNTIME = ['r18dev', 'fanza']
    FIELD_PRIORITY_DESCRIPTION = ['r18dev', 'fanza']
    FIELD_PRIORITY_COVER = ['r18dev', 'fanza']
    FIELD_PRIORITY_POSTER = ['r18dev', 'fanza']
    FIELD_PRIORITY_GALLERY = ['r18dev', 'fanza']
    
    # Scraper merge strategy: 'priority' (use first available) or 'merge' (combine data)
    SCRAPER_MERGE_STRATEGY = os.getenv("SCRAPER_MERGE_STRATEGY", "priority")
    
    # Required Fields Validation
    # Fields that must be present in metadata for processing to continue
    # If any of these fields are missing or empty, the video file will be skipped
    REQUIRED_FIELDS = ['id', 'title', 'year']
    REQUIRED_FIELDS_ENABLED = os.getenv("REQUIRED_FIELDS_ENABLED", "true").lower() == "true"
    
    # File Patterns
    #JAV_CODE_PATTERN = r'[A-Za-z]{2,6}[-]?\d{3,5}'
    JAV_CODE_PATTERN = r'[A-Za-z0-9]{2,6}-?\d{3,5}'
    VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mkv', '.wmv', '.mov']
    
    # NFO Template Settings
    NFO_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<movie>
    <title>[{id}] {title}</title>
    <originaltitle>{original_title}</originaltitle>
    <sorttitle>{sort_title}</sorttitle>  
    <id>{id}</id>
    <releasedate>{release_date}</releasedate>
    <year>{year}</year>
    <runtime>{runtime}</runtime>
    <mpaa>{mpaa}</mpaa>
    {director_tags}
    <studio>{studio}</studio>
    <rating>{rating}</rating>
    <votes>{votes}</votes>
    <plot>{plot}</plot>
    <outline>{outline}</outline>
    <tagline>{tagline}</tagline>
    <set>{series}</set>
    <label>{label}</label>
    {genre_tags}
    {actor_tags}
    <thumb>{poster}</thumb>
    <fanart>
        <thumb>{cover}</thumb>
    </fanart>
</movie>"""

# Global settings instance
settings = Settings()
