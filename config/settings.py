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
    OUTPUT_DIR_TEMPLATE = os.getenv("OUTPUT_DIR_TEMPLATE", "<YEAR>/<ID>")
    
    # Translation Settings
    TRANSLATION_ENABLED = os.getenv("TRANSLATION_ENABLED", "false").lower() == "true"
    TRANSLATION_API_KEY = os.getenv("TRANSLATION_API_KEY", "")
    TRANSLATION_SERVICE = os.getenv("TRANSLATION_SERVICE", "google")  # google, deepl, etc.
    TRANSLATION_TARGET_LANG = os.getenv("TRANSLATION_TARGET_LANG", "en")
    TRANSLATION_SOURCE_LANG = os.getenv("TRANSLATION_SOURCE_LANG", "ja")
    
    # Fields to translate (comma-separated)
    TRANSLATION_FIELDS = os.getenv("TRANSLATION_FIELDS", "title,plot,genres,actress,director,studio,label,series").split(",")
    
    # Genres to skip (comma-separated)
    SKIP_GENRES = os.getenv("SKIP_GENRES", "4K,ハイビジョン,独占配信").split(",")
    
    # Cache settings
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_FILE = os.getenv("CACHE_FILE", "")  # Empty for default location
    
    # File Patterns
    JAV_CODE_PATTERN = r'[A-Za-z]{2,5}[-]?\d{3,5}'
    VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mkv', '.wmv', '.mov']
    
    # NFO Template Settings
    NFO_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<movie>
    <title>{title}</title>
    <originaltitle>{original_title}</originaltitle>
    <sorttitle>{sort_title}</sorttitle>
    <set>{series}</set>
    <year>{year}</year>
    <rating>{rating}</rating>
    <votes>{votes}</votes>
    <releasedate>{release_date}</releasedate>
    <runtime>{runtime}</runtime>
    <country>{country}</country>
    <mpaa>{mpaa}</mpaa>
    <id>{jav_id}</id>
    <uniqueid type="jav" default="true">{jav_id}</uniqueid>
    <uniqueid type="content_id">{content_id}</uniqueid>
    <plot>{plot}</plot>
    <outline>{outline}</outline>
    <tagline>{tagline}</tagline>
    <director>{director}</director>
    <studio>{studio}</studio>
    <label>{label}</label>
{genre_tags}
{actor_tags}
    <thumb aspect="poster">{poster}</thumb>
    <thumb aspect="cover">{cover}</thumb>
    <fanart>
        <thumb>{fanart}</thumb>
    </fanart>
</movie>"""

# Global settings instance
settings = Settings() 