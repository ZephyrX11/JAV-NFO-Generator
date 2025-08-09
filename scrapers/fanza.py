import json
from typing import Dict, Optional, Any, List
from .base import BaseScraper
from config.settings import settings
from utils.pattern import PatternMatcher

class FanzaScraper(BaseScraper):
    """Fanza scraper implementation."""
    
    def __init__(self):
        super().__init__()
        self.api_url = settings.FANZA_API_URL
    
    def get_name(self) -> str:
        return "Fanza"
    
    def search(self, jav_code: str) -> Optional[Dict[str, Any]]:
        """
        Search for metadata using Fanza GraphQL API.
        
        Args:
            jav_code: The JAV code to search for
            
        Returns:
            Dictionary with metadata or None if not found
        """
        # Convert JAV code to content ID for Fanza API
        content_id = PatternMatcher.jav_code_to_content_id(jav_code)
        
        payload = {
            "operationName": "ContentPageData",
            "query": """
            query ContentPageData($id: ID!) {
             ppvContent(id: $id) {
              id
              floor
              title
              releaseStatus
              description
              packageImage {
                largeUrl
                mediumUrl
              }
              sampleImages {
                number
                imageUrl
                largeImageUrl
              }
              deliveryStartDate
              makerReleasedAt
              duration
              actresses {
                id
                name
                nameRuby
                imageUrl
              }
              directors {
                id
                name
              }
              series {
                id
                name
              }
              maker {
                id
                name
              }
              label {
                id
                name
              }
              genres {
                id
                name
              }
              contentType
              makerContentId
              }
              reviewSummary(contentId: $id) {
                average
                total
                withCommentTotal
              }
            }
            """,
            "variables": {
                "id": content_id
            }
        }
        
        response = self._make_request(
            self.api_url,
            method='POST',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if not response or not self.validate_response(response):
            return None
        
        try:
            data = response.json()
            return self.format_metadata(data)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON response for {jav_code}")
            return None
    
    def format_metadata(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format Fanza API response into standard metadata format.
        
        Args:
            raw_data: Raw API response
            
        Returns:
            Formatted metadata
        """
        try:
            content = raw_data.get('data', {}).get('ppvContent', {})
            if not content:
                return {}

            # Extract basic info
            title = content.get('title', '')
            description = content.get('description', '')
            duration = content.get('duration', 0)
            
            # Extract release date
            release_date = content.get('deliveryStartDate', '')
            if release_date:
                release_date = release_date.split('T')[0]  # Get date part only
            
            # Extract directors
            directors = [director["name"] for director in content.get('directors', [])]
            
            # Extract series
            series = content.get('series', {})
            series_name = series.get('name', '') if series else ''
            
            # Extract maker and label
            maker = content.get('maker', {})
            maker_name = maker.get('name', '') if maker else ''
            
            label = content.get('label', {})
            label_name = label.get('name', '') if label else ''
            
            # Extract genres and actresses as arrays
            genres = [genre["name"] for genre in content.get("genres", [])]
            actresses = [
                {"name": a.get("name", ""), "image": a.get("imageUrl", "")}
                for a in content.get("actresses", [])
            ]
            # Filter genres
            #genres_str = ', '.join(genre_names) if genre_names else ''
            #filtered_genres = PatternMatcher.filter_genres(genres_str)

            # Extract images
            package_image = content.get('packageImage', {})
            cover_url = package_image.get('largeUrl', '') if package_image else ''
            poster_url = package_image.get('mediumUrl', '') if package_image else ''
            
            sample_images = content.get('sampleImages', [])
            fanart_urls = [img.get('largeImageUrl', '') for img in sample_images if img.get('largeImageUrl')]
            
            # Format duration
            runtime = f"{duration // 60}" if duration else "0:00"
            
            # Get content ID and JAV ID
            content_id = content.get('id', '').lower()
            jav_id = content.get('makerContentId', '')
            
            # Extract rating info
            review = raw_data.get('data', {}).get('reviewSummary', {})
            rating = review.get('average', '')  # Use float or format as string
            votes = review.get('total', '')     # Total number of votes

            return {
                'title': title,
                'original_title': title,
                'sort_title': title,
                'plot': description,
                'outline': description[:100] + '...' if len(description) > 100 else description,
                'tagline': '',
                'year': release_date.split('-')[0] if release_date else '',
                'release_date': release_date,
                'runtime': runtime,
                'rating': rating,
                'votes': votes,
                'id': jav_id,
                'content_id': content_id,
                'directors': directors,
                'studio': maker_name,
                'label': label_name,
                'series': series_name,
                'genres': genres,
                'actresses': actresses,
                'cover': cover_url,
                'poster': poster_url,
                'fanart': fanart_urls[0] if fanart_urls else '',
                'sample_images': fanart_urls,
                'raw_data': raw_data
            }
            
        except Exception as e:
            print(f"Error formatting metadata: {e}")
            return {}