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
            primary_title = raw_data.get('title_en') or ''
            secondary_title = raw_data.get('title_ja') or ''
            directors = [d.get('name_romaji', '') for d in raw_data.get('directors', []) if d.get('name_romaji')]
            label = raw_data.get('label_name_en') or ''
            categories = [category['name_en'] for category in raw_data.get('categories', [])]
            series = raw_data.get('series_name_en') or ''
            maker = raw_data.get('maker_name_en') or ''
            actresses = [
                {'name': a.get('name_romaji', '') or '', 'image': IMAGE_BASE_URL + a['image_url'] if a.get('image_url') else ''}
                for a in raw_data.get('actresses', [])
            ]
        else:
            primary_title = raw_data.get('title_ja') or ''
            secondary_title = raw_data.get('title_en') or ''
            directors = [d.get('name_kanji', '') for d in raw_data.get('directors', []) if d.get('name_kanji')]
            label = raw_data.get('label_name_ja') or ''
            categories = [category['name_ja'] for category in raw_data.get('categories', [])]
            series = raw_data.get('series_name_ja') or ''
            maker = raw_data.get('maker_name_ja') or ''
            actresses = [
                {'name': a.get('name_kanji', '') or '', 'image': IMAGE_BASE_URL + a['image_url'] if a.get('image_url') else ''}
                for a in raw_data.get('actresses', [])
            ]
            
        metadata = {
            'source': 'r18.dev',
            'content_id': raw_data.get('content_id') or '',
            'id': raw_data.get('dvd_id') or '',
            'title': primary_title,
            'title_en': raw_data.get('title_en') or '',
            'title_jp': raw_data.get('title_ja') or '',
            'original_title': raw_data.get('title_ja') or '',
            'release_date': raw_data.get('release_date') or '',
            'year': (raw_data.get('release_date') or '').split('-')[0] if raw_data.get('release_date') else '',
            'runtime': raw_data.get('runtime_mins', 0),
            'description': raw_data.get('comment_en') or '',
            'cover': raw_data.get('jacket_full_url') or '',
            'poster': raw_data.get('jacket_thumb_url') or '',
            'sample_url': raw_data.get('sample_url') or '',
            'actresses': actresses,
            'directors': directors,
            'genres': categories,
            'studio': maker,
            'label': label,
            'series': series,
            'gallery': self._format_gallery(raw_data.get('gallery', []))
        }
        
        return metadata
    def _format_gallery(self, gallery: List[Dict[str, Any]]) -> List[str]:
        """Return only the full-size gallery images."""
        return [img["image_full"] for img in gallery if img.get("image_full")]

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
