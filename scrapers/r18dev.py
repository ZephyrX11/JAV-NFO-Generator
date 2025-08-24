import json
from typing import Dict, Optional, Any, List
from .base import BaseScraper
from config.settings import settings
from utils.pattern import PatternMatcher

class R18DevScraper(BaseScraper):
    """R18.dev JSON API scraper implementation."""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://r18.dev/videos/vod/movies/detail/-/combined={}/json"
    
    def get_name(self) -> str:
        return "R18.dev"
    
    def search(self, jav_code: str) -> Optional[Dict[str, Any]]:
        """
        Search for metadata using R18.dev JSON API.
        
        Args:
            jav_code: The JAV code to search for
            
        Returns:
            Dictionary with metadata or None if not found
        """
        # Convert JAV code to content ID for R18.dev API
        content_id = PatternMatcher.jav_code_to_content_id(jav_code)
        # content_id = jav_code.lower().replace("-", "")
        
        # Build API URL
        url = self.base_url.format(content_id)
        
        # Make request
        response = self._make_request(url)
        if not response:
            return None
        
        try:
            data = response.json()
            
            # Check if we got valid data
            if not data or not data.get('content_id'):
                return None
            
            # Format the metadata
            return self.format_metadata(data)
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            return None
        except Exception as e:
            print(f"Error processing R18.dev response: {e}")
            return None
    
    def format_metadata(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format raw R18.dev metadata into standard format.
        
        Args:
            raw_data: Raw metadata from R18.dev API
            
        Returns:
            Formatted metadata dictionary
        """
        # Determine language preference
        use_english = settings.R18DEV_LANGUAGE.lower() == "en"
        IMAGE_BASE_URL = "https://awsimgsrc.dmm.co.jp/pics_dig/mono/actjpgs/"

        # Select title based on language preference
        if use_english:
            primary_title = raw_data.get('title_en', '') or raw_data.get('title_ja', '')
            secondary_title = raw_data.get('title_ja', '')
            directors = [director["name_romaji"] for director in raw_data.get('directors', [])]
            label = raw_data.get('label_name_en', '')
            categories = [category['name_en'] for category in raw_data.get('categories', [])]
            series = raw_data.get('series_name_en', '')
            maker = raw_data.get('maker_name_en', '')
            actresses = [
                {"name": a.get("name_romaji", "") or "","image": IMAGE_BASE_URL + a["image_url"] if a.get("image_url") else ""}
                for a in raw_data.get("actresses", [])
            ]
        else:
            primary_title = raw_data.get('title_ja', '') or raw_data.get('title_en', '')
            secondary_title = raw_data.get('title_en', '')
            directors = [director["name_kanji"] for director in raw_data.get('directors', [])]
            label = raw_data.get('label_name_ja', '')
            categories = [category['name_ja'] for category in raw_data.get('categories', [])]
            series = raw_data.get('series_name_ja', '')
            maker = raw_data.get('maker_name_ja', '')
            actresses = [
                {"name": a.get("name_kanji", "") or "", "image": IMAGE_BASE_URL + a["image_url"] if a.get("image_url") else ""}
                for a in raw_data.get("actresses", [])
            ]
            
        metadata = {
            'source': 'r18.dev',
            'content_id': raw_data.get('content_id', ''),
            'id': raw_data.get('dvd_id', ''),
            'title': primary_title,
            'title_en': raw_data.get('title_en', ''),
            'title_jp': raw_data.get('title_ja', ''),
            'original_title': raw_data.get('title_ja', ''),
            'release_date': raw_data.get('release_date', ''),
            'year': raw_data.get('release_date', '').split('-')[0] if raw_data.get('release_date', '') else '',
            'runtime': raw_data.get('runtime_mins', 0),
            'description': raw_data.get('comment_en', ''),
            'cover_url': raw_data.get('jacket_full_url', ''),
            'poster_url': raw_data.get('jacket_thumb_url', ''),
            'sample_url': raw_data.get('sample_url', ''),
            'actresses': actresses,
            'directors': directors,
            'genres': categories,
            'studio': maker,
            'label': label,
            'series': series,
            'gallery': self._format_gallery(raw_data.get('gallery', []))
        }
        
        return metadata
    
    def _format_gallery(self, gallery: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Format gallery/sample images data."""
        formatted = []
        for image in gallery:
            formatted.append({
                'full_url': image.get('image_full', ''),
                'thumb_url': image.get('image_thumb', '')
            })
        return formatted
    
    def validate_response(self, response) -> bool:
        """
        Validate if response contains valid R18.dev data.
        
        Args:
            response: HTTP response
            
        Returns:
            True if response is valid, False otherwise
        """
        try:
            data = response.json()
            return bool(data and data.get('content_id'))
        except (json.JSONDecodeError, AttributeError):
            return False
